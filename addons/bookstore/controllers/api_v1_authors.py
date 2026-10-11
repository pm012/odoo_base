import logging

from odoo import http
from odoo.http import request

from .common import ApiMixin

_logger = logging.getLogger(__name__)


class ApiV1Authors(http.Controller, ApiMixin):
    """
    REST API v1 for authors.

    Endpoints:
        GET    /api/v1/authors              — list of authors
        GET    /api/v1/authors/<id>         — a single author
        POST   /api/v1/authors              — create an author
        PUT    /api/v1/authors/<id>         — update an author
        DELETE /api/v1/authors/<id>         — delete an author

    For external clients (mobile apps, SPA, integrations).
    For internal Odoo clients — JSON-RPC at /api/authors.
    """

    MODEL = 'bookstore.author'

    # =========================================================
    # GET /api/v1/authors
    # =========================================================

    @http.route(
        '/api/v1/authors',
        type='http', auth='public', methods=['GET'], csrf=False,
    )
    def list_authors(self, limit=None, offset=0, include_books=False, **kwargs):
        """
        GET /api/v1/authors?limit=10&offset=0&include_books=true

        Query params:
            limit (int, optional)         — maximum number of records
            offset (int, default=0)       — offset value
            include_books (bool, optional) — whether to include books relation
        """
        limit, error = self._parse_int(limit, 'limit', default=None)
        if error:
            return error
        offset, error = self._parse_int(offset, 'offset', default=0)
        if error:
            return error

        include_books = str(include_books).lower() in ('1', 'true', 'yes')

        data = request.env[self.MODEL].sudo().get_authors_data(
            limit=limit,
            offset=offset,
            include_books=include_books,
        )
        return self._success(data)

    # =========================================================
    # GET /api/v1/authors/<id>
    # =========================================================

    @http.route(
        '/api/v1/authors/<int:author_id>',
        type='http', auth='public', methods=['GET'], csrf=False,
    )
    def get_author(self, author_id, include_books=False, **kwargs):
        """
        GET /api/v1/authors/1?include_books=true
        """
        include_books = str(include_books).lower() in ('1', 'true', 'yes')

        author = request.env[self.MODEL].sudo().browse(author_id)
        if not author.exists():
            return self._error('Author not found', status=404, extra={'author_id': author_id})

        return self._success(author.to_api_dict(include_books=include_books))

    # =========================================================
    # POST /api/v1/authors
    # =========================================================

    @http.route(
        '/api/v1/authors',
        type='http', auth='public', methods=['POST'], csrf=False,
    )
    def create_author(self, **kwargs):
        """
        POST /api/v1/authors

        JSON payload:
        {
            "name": "George Orwell",
            "biography": "...",
            "birth_date": "1903-06-25"
        }
        """
        payload, error = self._parse_json_body()
        if error:
            return error

        try:
            author_data = request.env[self.MODEL].sudo().create_from_api(payload)
        except ValueError as e:
            return self._error(str(e), status=400)

        return self._success(author_data, status=201)

    # =========================================================
    # PUT /api/v1/authors/<id>
    # =========================================================

    @http.route(
        '/api/v1/authors/<int:author_id>',
        type='http', auth='public', methods=['PUT'], csrf=False,
    )
    def update_author(self, author_id, **kwargs):
        """
        PUT /api/v1/authors/1

        JSON payload (any subset of fields):
        {
            "name": "New Name",
            "birth_date": "1903-06-25"
        }
        """
        author = request.env[self.MODEL].sudo().browse(author_id)
        if not author.exists():
            return self._error('Author not found', status=404, extra={'author_id': author_id})

        payload, error = self._parse_json_body()
        if error:
            return error

        try:
            author.write_from_api(payload)
        except ValueError as e:
            return self._error(str(e), status=400)

        return self._success(author.to_api_dict())

    # =========================================================
    # DELETE /api/v1/authors/<id>
    # =========================================================

    @http.route(
        '/api/v1/authors/<int:author_id>',
        type='http', auth='public', methods=['DELETE'], csrf=False,
    )
    def delete_author(self, author_id, **kwargs):
        """
        DELETE /api/v1/authors/1

        Deletes the author. If the author has books, Odoo will raise an error
        (due to ondelete='restrict' configuration on book.author_id).
        """
        author = request.env[self.MODEL].sudo().browse(author_id)
        if not author.exists():
            return self._error('Author not found', status=404, extra={'author_id': author_id})

        try:
            author.unlink()
        except Exception as e:
            _logger.exception("API: failed to delete author %s", author_id)
            return self._error(
                f'Cannot delete author: {e}',
                status=400,
                extra={'author_id': author_id},
            )

        return self._success({'success': True, 'deleted_id': author_id})
