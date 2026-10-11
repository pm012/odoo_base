"""
REST API v1 for books.
Endpoints:
    GET    /api/v1/books              — list of books
    GET    /api/v1/books/<id>         — a single book
    POST   /api/v1/books              — create a book
    PUT    /api/v1/books/<id>         — update a book
    DELETE /api/v1/books/<id>         — delete a book
    
Business logic is already partially implemented in the bookstore.book model —
there are methods like get_books_data, create_from_api, write_from_api, and to_dict.

For JSON-RPC (Odoo clients) — /api/books through book_api.py.
"""