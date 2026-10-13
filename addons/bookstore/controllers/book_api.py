import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class BookstoreApi(http.Controller):
    """
    REST API for each shop.

    All endpoints start with /api/. Authentication - public,
    e.g.  access without login. For tutorial purpose is - ok.
    In prod token or API key should be added.
    """

    # =========================================================
    # GET-ish enpoints (via type='json', Odoo-way)
    # =========================================================

    @http.route('/api/books', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def list_books(self, limit=10, offset=0, **kwargs):
        """
        The list of books.

        Returns JSON-RPC-wrapper:
        {
            "jsonrpc": "2.0",
            "result": {
                "count": 4,
                "books": [...]
            },
            "id": null
        }

        Parameters (are passed in  a JSON-body):
        - limit: int - how many books should be returned
        - offset: int — which book should be initial
        """
        _logger.info("API: list_books called with limit=%s offset=%s", limit, offset)

        Book = request.env['bookstore.book'].sudo()
        domain = [('active', '=', True)]

        total = Book.search_count(domain)
        books = Book.search(domain, limit=limit, offset=offset)

        return {
            'count': total,
            'limit': limit,
            'offset': offset,
            'books': [self._serialize_book(b) for b in books],
        }

    @http.route('/api/books/<int:book_id>', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def get_book(self, book_id, **kwargs):
        """
        Get one book by ID.

        If not found - will return {'error': 'Book not found'}.
        """
        _logger.info("API: get_book called with book_id=%s", book_id)

        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists():
            return {'error': 'Book not found', 'book_id': book_id}

        return {'book': self._serialize_book(book)}


     #========================================================
     #Delete book by ID
     #========================================================
    @http.route('/api/books/<int:book_id>/delete', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def delete_book(self, book_id, **kwargs):
        """
        Delete one book by ID.  
        """
        _logger.info("API: delete_book called with book_id=%s", book_id)
        # Check if the book exists
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists():
            return {'error': 'Book not found', 'book_id': book_id}
        
        # Delete the book
        try:
            book.unlink()
        except Exception as e:
            _logger.exception("API: failed to delete book %s", book_id)
            return {'error': f'Cannot delete book: {e}', 'book_id': book_id}
        return {'success': True, 'message': f'Book with ID {book_id} has been deleted.'}


    # Sample of combination pure rest and odoo rpc
    @http.route('/api/authors', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def list_authors(self, **kwargs):
        """
        List of authors. Logic is completely delegated to the model.
        """
        _logger.info("API: list_authors called with kwargs=%s", kwargs)
        
        # Call model method. Use .sudo() 
        # for public access as we discussed before.
        # Pass params with kwargs.
        limit = kwargs.get('limit')
        offset = kwargs.get('offset', 0)
        
        # Call logic, that is located in the model. NOTE!!!! This is (.sudo()) dangerous (acceptible for sandboxing, but should be hidden under auth logic in PROD)
        data = request.env['bookstore.author'].sudo().get_authors_data(
            limit=limit, 
            offset=offset
        )
        
        return data

    # =========================================================
    # POST with JSON-body (via type='http', classical REST)
    # =========================================================

    @http.route('/api/books/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_book(self, **kwargs):
        """
        Create a book from the JSON-body request.
        
        Expected JSON:
        {
            "name": "New Book",
            "price": 19.99,
            "quantity": 5,
            "author_id": 1,
            "isbn": "978-0-13-235088-4"
        }
        """
        _logger.info("API: create_book called")

        try:
            data = json.loads(request.httprequest.data)
        except (ValueError, TypeError) as e:
            return self._json_response({'error': f'Invalid JSON: {e}'}, status=400)

        if not data.get('name'):
            return self._json_response({'error': 'Field "name" is required'}, status=400)

        try:
            book = request.env['bookstore.book'].sudo().create({
                'name': data['name'],
                'price': data.get('price', 0.0),
                'quantity': data.get('quantity', 0),
                'author_id': data.get('author_id'),
                'isbn': data.get('isbn'),
                'description': data.get('description', ''),
            })
        except Exception as e:
            _logger.exception("API: create_book failed")
            return self._json_response({'error': str(e)}, status=400)

        return self._json_response({
            'success': True,
            'book': self._serialize_book(book),
        }, status=201)

    # =========================================================
    # Helpers
    # =========================================================

    def _serialize_book(self, book):
        """Returns recordset of book in dict for JSON."""
        return {
            'id': book.id,
            'name': book.name,
            'author': book.author_id.name if book.author_id else None,
            'author_id': book.author_id.id if book.author_id else None,
            'price': book.price,
            'quantity': book.quantity,
            'total_value': book.total_value,
            'isbn': book.isbn,
            'genres': [g.name for g in book.genre_ids],
            'active': book.active,
        }

    def _json_response(self, data, status=200):
        """Builds HTTP-response with JSON and defined status."""
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
            status=status,
        )

### Sample of combination pure rest and odoo rpc (for odoo developers) - see list_authors() method above.