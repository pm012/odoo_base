import json

from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestBookApi(HttpCase):
    """
    Тести HTTP API (REST).

    HttpCase doing real HTTP-requests to Odoo.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = cls.env['bookstore.author'].create({'name': 'API Test Author'})

    # =========================================================
    # GET /api/v1/authors
    # =========================================================

    def test_get_authors_list(self):
        """GET /api/v1/authors -> 200, JSON with the list."""
        response = self.url_open(
            '/api/v1/authors',
            method='GET',
            headers={'Content-Type': 'application/json'},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('authors', data)
        self.assertIn('count', data)

    def test_get_author_by_id(self):
        """GET /api/v1/authors/<id> -> 200."""
        url = f'/api/v1/authors/{self.author.id}'
        response = self.url_open(url, method='GET')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.author.id)
        self.assertEqual(data['name'], 'API Test Author')

    def test_get_author_not_found(self):
        """GET /api/v1/authors/999999 -> 404."""
        response = self.url_open('/api/v1/authors/999999', method='GET')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)

    # =========================================================
    # POST /api/v1/authors
    # =========================================================

    def test_create_author_success(self):
        """POST /api/v1/authors -> 201."""
        payload = {'name': 'New API Author', 'biography': 'Test'}
        response = self.url_open(
            '/api/v1/authors',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'New API Author')

        # Перевірка в БД
        author = self.env['bookstore.author'].browse(data['id'])
        self.assertTrue(author.exists())

    def test_create_author_without_name(self):
        """POST /api/v1/authors без name -> 400."""
        response = self.url_open(
            '/api/v1/authors',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'biography': 'No name'}),
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_create_author_invalid_date(self):
        """POST /api/v1/authors with the date in the future -> 400."""
        payload = {
            'name': 'Future Author',
            'birth_date': '2099-01-01',
        }
        response = self.url_open(
            '/api/v1/authors',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 400)

    # =========================================================
    # CRUTIAL TEST: savepoint / rollback
    # =========================================================

    def test_create_book_negative_price_does_not_persist(self):
        """
         CRITICAL TEST: tests the bug with rollback when invalid value is set (e.g. negative price).

        POST /api/books/create з price < 0:
        - should return 400
        - the book should NOT be created in the database (savepoint working)

        Without  savepoint - the book will be created and that's the bug.
        """
        payload = {
            'name': 'Bad Book Savepoint Test',
            'price': -28.0,
            'quantity': 3,
            'isbn': '978-0-13-235088-4',
        }
        response = self.url_open(
            '/api/books/create',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 400, "Має бути 400")

        # Main test: the book should not be present in the DB
        book = self.env['bookstore.book'].search([
            ('name', '=', 'Bad Book Savepoint Test'),
        ])
        self.assertFalse(
            book,
            f"The book with negative price created! "
            f"savepoint don't work. Found: {book.mapped('name')}"
        )

    def test_create_book_valid_price_persists(self):
        """POST /api/books/create with valid price -> 201, the book is created."""
        payload = {
            'name': 'Good Book API Test',
            'price': 19.99,
            'quantity': 2,
            'isbn': '9780132350884',
        }
        response = self.url_open(
            '/api/books/create',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 201)

        book = self.env['bookstore.book'].search([
            ('name', '=', 'Good Book API Test'),
        ])
        self.assertTrue(book, "The book should be created")
        self.assertEqual(book.price, 19.99)

    # =========================================================
    # GET /api/v1/partners
    # =========================================================

    def test_get_partners_list(self):
        """GET /api/v1/partners -> 200."""
        response = self.url_open('/api/v1/partners', method='GET')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('partners', data)
        self.assertIn('count', data)

    def test_get_partner_not_found(self):
        """GET /api/v1/partners/999999 -> 404."""
        response = self.url_open('/api/v1/partners/999999', method='GET')
        self.assertEqual(response.status_code, 404)