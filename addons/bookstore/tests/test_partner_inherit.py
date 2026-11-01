from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPartnerInherit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.genres = cls.env['bookstore.genre']
        for i in range(7):
            cls.genres |= cls.env['bookstore.genre'].create({'name': f'Genre {i}'})

    def test_field_exists(self):
        """Input favorite_genre_ids exists on res.partner."""
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.assertIn('favorite_genre_ids', partner._fields)

    def test_create_with_genres(self):
        """Partner is created with genres."""
        partner = self.env['res.partner'].create({
            'name': 'Partner with Genres',
            'favorite_genre_ids': [(6, 0, self.genres[:2].ids)],
        })
        self.assertEqual(len(partner.favorite_genre_ids), 2)

    def test_max_5_genres_constraint(self):
        """More than 5 genresв -> ValidationError."""
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        with self.assertRaises(ValidationError):
            partner.write({
                'favorite_genre_ids': [(6, 0, self.genres[:6].ids)],
            })

    def test_exactly_5_genres_is_valid(self):
        """Exactly 5 genres - valid."""
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        partner.write({
            'favorite_genre_ids': [(6, 0, self.genres[:5].ids)],
        })
        self.assertEqual(len(partner.favorite_genre_ids), 5)

    def test_search_by_genre(self):
        """Search partners by genre."""
        genre = self.genres[0]
        partner1 = self.env['res.partner'].create({
            'name': 'Partner 1',
            'favorite_genre_ids': [(6, 0, [genre.id])],
        })
        partner2 = self.env['res.partner'].create({
            'name': 'Partner 2',
            'favorite_genre_ids': [(6, 0, [self.genres[1].id])],
        })

        found = self.env['res.partner'].search([
            ('favorite_genre_ids', 'in', genre.id)
        ])
        self.assertIn(partner1, found)
        self.assertNotIn(partner2, found)