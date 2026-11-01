from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBookModel(TransactionCase):
    """
    Tets for model bookstore.book.

    @tagged('post_install', '-at_install'):
    - post_install: launch AFTER the module installation
    - -at_install: DON'T launch during installation
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create the author once for all tests
        cls.author = cls.env['bookstore.author'].create({
            'name': 'Test Author',
        })
        # Create genre
        cls.genre = cls.env['bookstore.genre'].create({
            'name': 'Test Genre',
        })

    def _create_book(self, **kwargs):
        """Helper: creates book with the default values."""
        vals = {
            'name': 'Test Book',
            'author_id': self.author.id,
            'price': 10.0,
            'quantity': 5,
            'isbn': '978-0-13-235088-4',
        }
        vals.update(kwargs)
        return self.env['bookstore.book'].create(vals)

    # =========================================================
    # Computed fields
    # =========================================================

    def test_compute_total_value(self):
        """total_value = price * quantity."""
        book = self._create_book(price=10.0, quantity=5)
        self.assertEqual(book.total_value, 50.0) 

    def test_compute_total_value_updates_on_write(self):
        """On price change — total_value should be recalculated."""
        book = self._create_book(price=10.0, quantity=5)
        self.assertEqual(book.total_value, 50.0)

        book.write({'price': 20.0})
        self.assertEqual(book.total_value, 100.0)

    def test_compute_total_value_zero_quantity(self):
        """If quantity=0 — total_value=0."""
        book = self._create_book(price=10.0, quantity=0)
        self.assertEqual(book.total_value, 0.0)

    # =========================================================
    # Constraints: price
    # =========================================================

    def test_price_negative_raises(self):
        """Ціна < 0 → ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_book(price=-10.0)

    def test_price_negative_on_write_raises(self):
        """When updated to the negative price getting ->  ValidationError."""
        book = self._create_book(price=10.0)
        with self.assertRaises(ValidationError):
            book.write({'price': -5.0})

    def test_price_zero_is_valid(self):
        """Ціна = 0 — валідна."""
        book = self._create_book(price=0.0)
        self.assertEqual(book.price, 0.0)

    # =========================================================
    # Constraints: quantity
    # =========================================================

    def test_quantity_negative_raises(self):
        """Кількість < 0 → ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_book(quantity=-1)

    # =========================================================
    # Constraints: ISBN
    # =========================================================

    def test_isbn_empty_is_valid(self):
        """Empty ISBN - valid (the field is not required)."""
        book = self._create_book(isbn=False)
        self.assertFalse(book.isbn)

    def test_isbn_13_valid(self):
        """ISBN-13 — валідний."""
        book = self._create_book(isbn='9780132350884')
        self.assertEqual(book.isbn, '9780132350884')

    def test_isbn_10_valid(self):
        """ISBN-10 — валідний."""
        book = self._create_book(isbn='0306406152')
        self.assertEqual(book.isbn, '0306406152')

    def test_isbn_10_with_x_valid(self):
        """ISBN-10 with  X at the end - is valid."""
        book = self._create_book(isbn='097522980X')
        self.assertEqual(book.isbn, '097522980X')

    def test_isbn_with_hyphens_valid(self):
        """ISBN with hyphens - valid (normalizing)."""
        book = self._create_book(isbn='978-0-13-235088-4')
        self.assertEqual(book.isbn, '978-0-13-235088-4')

    def test_isbn_invalid_raises(self):
        """Invalid ISBN → ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_book(isbn='12345')

    def test_isbn_letters_raises(self):
        """ISBN with letters (except X at the end) -> ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_book(isbn='abcdefghij')

    # =========================================================
    # Many2many: genres
    # =========================================================

    def test_genre_ids(self):
        """The  book could have genres."""
        book = self._create_book(genre_ids=[(6, 0, [self.genre.id])])
        self.assertEqual(len(book.genre_ids), 1)
        self.assertEqual(book.genre_ids.name, 'Test Genre')

    # =========================================================
    # Active field
    # =========================================================

    def test_default_active(self):
        """By default the book is active."""
        book = self._create_book()
        self.assertTrue(book.active)

    def test_archive(self):
        """Archive (active=False)."""
        book = self._create_book()
        book.write({'active': False})
        self.assertFalse(book.active)