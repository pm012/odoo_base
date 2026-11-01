from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAuthorModel(TransactionCase):

    # =========================================================
    # Constraints
    # =========================================================

    def test_birth_date_past_is_valid(self):
        """Date of birth in the past - is valid."""
        author = self.env['bookstore.author'].create({
            'name': 'Old Author',
            'birth_date': date(1900, 1, 1),
        })
        self.assertTrue(author.birth_date)

    def test_birth_date_today_is_valid(self):
        """Todays date of birth - is valid."""
        today = date.today()
        author = self.env['bookstore.author'].create({
            'name': 'Today Author',
            'birth_date': today,
        })
        self.assertEqual(author.birth_date, today)

    def test_birth_date_future_raises(self):
        """Date of birth in the future -> ValidationError."""
        future = date.today() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.env['bookstore.author'].create({
                'name': 'Future Author',
                'birth_date': future,
            })

    def test_birth_date_empty_is_valid(self):
        """Empty дата - valid."""
        author = self.env['bookstore.author'].create({
            'name': 'No Date Author',
        })
        self.assertFalse(author.birth_date)

    # =========================================================
    # get_authors_data (API method)
    # =========================================================

    def test_get_authors_data_returns_dict(self):
        """get_authors_data returns dict with keys."""
        self.env['bookstore.author'].create({'name': 'Author A'})
        self.env['bookstore.author'].create({'name': 'Author B'})

        result = self.env['bookstore.author'].get_authors_data()

        self.assertIsInstance(result, dict)
        self.assertIn('count', result)
        self.assertIn('authors', result)
        self.assertGreaterEqual(result['count'], 2)

    def test_get_authors_data_limit(self):
        """limit обмежує кількість записів."""
        # Clear not existent
        #self.env['bookstore.author'].search([]).unlink()
        initial_count = self.env['bookstore.author'].search_count([])
        for i in range(5):
            self.env['bookstore.author'].create({'name': f'Author Limit Test {i}'})

        result = self.env['bookstore.author'].get_authors_data(limit=3)
        self.assertEqual(len(result['authors']), 3)
        # Overal quantity = initial quantity + 5        
        self.assertEqual(result['count'], initial_count + 5)

    # =========================================================
    # create_from_api
    # =========================================================

    def test_create_from_api_success(self):
        """create_from_api creates the author."""
        result = self.env['bookstore.author'].create_from_api({
            'name': 'API Author',
            'biography': 'Test bio',
        })
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'API Author')
        self.assertEqual(result['biography'], 'Test bio')

        # Verify in the database
        author = self.env['bookstore.author'].browse(result['id'])
        self.assertTrue(author.exists())

    def test_create_from_api_without_name_raises(self):
        """create_from_api without name -> ValueError."""
        with self.assertRaises(ValueError):
            self.env['bookstore.author'].create_from_api({'biography': 'No name'})

    def test_create_from_api_empty_name_raises(self):
        """create_from_api with empty name -> ValueError."""
        with self.assertRaises(ValueError):
            self.env['bookstore.author'].create_from_api({'name': '   '})

    def test_create_from_api_invalid_date_raises(self):
        """create_from_api with date in the future -> ValueError."""
        future = (date.today() + timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            self.env['bookstore.author'].create_from_api({
                'name': 'Future API Author',
                'birth_date': future,
            })

    # =========================================================
    # write_from_api
    # =========================================================

    def test_write_from_api_success(self):
        """write_from_api updates author."""
        author = self.env['bookstore.author'].create({'name': 'Original'})
        author.write_from_api({'name': 'Updated', 'biography': 'New bio'})
        self.assertEqual(author.name, 'Updated')
        self.assertEqual(author.biography, 'New bio')

    def test_write_from_api_empty_name_raises(self):
        """write_from_api with the empty name -> ValueError."""
        author = self.env['bookstore.author'].create({'name': 'Original'})
        with self.assertRaises(ValueError):
            author.write_from_api({'name': ''})