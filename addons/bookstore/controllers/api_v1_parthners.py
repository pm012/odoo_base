import logging

from odoo import http
from odoo.http import request

from .common import ApiMixin

_logger = logging.getLogger(__name__)


class ApiV1Partners(http.Controller, ApiMixin):
    """
    REST API v1 for parthners (contacts).

    Endpoints (read only):
        GET /api/v1/partners                 — list
        GET /api/v1/partners/<id>            — one parthner by id
        GET /api/v1/partners/<id>/genres     — only parthner genres

    NB!!! Mutations (POST/PUT/DELETE) not implemented proposely.
    Parthners are clients/suppliers, for mutations authentication is required.
    """

    MODEL = 'res.partner'

    # =========================================================
    # GET /api/v1/partners
    # =========================================================

    @http.route(
        '/api/v1/partners',
        type='http', auth='public', methods=['GET'], csrf=False,
    )
    def list_partners(self, limit=None, offset=0, genre_id=None, include_genres=True, **kwargs):
        """
        GET /api/v1/partners?limit=10&offset=0&genre_id=1&include_genres=true
        """
        limit, error = self._parse_int(limit, 'limit', default=None)
        if error:
            return error
        offset, error = self._parse_int(offset, 'offset', default=0)
        if error:
            return error
        genre_id, error = self._parse_int(genre_id, 'genre_id', default=None)
        if error:
            return error

        include_genres = str(include_genres).lower() in ('1', 'true', 'yes')

        data = request.env[self.MODEL].sudo().get_partners_data(
            limit=limit,
            offset=offset,
            genre_id=genre_id,
            include_genres=include_genres,
        )
        return self._success(data)

    # =========================================================
    # GET /api/v1/partners/<id>
    # =========================================================

    @http.route(
        '/api/v1/partners/<int:partner_id>',
        type='http', auth='public', methods=['GET'], csrf=False,
    )
    def get_partner(self, partner_id, include_genres=True, **kwargs):
        """
        GET /api/v1/partners/9?include_genres=true
        """
        include_genres = str(include_genres).lower() in ('1', 'true', 'yes')

        partner = request.env[self.MODEL].sudo().browse(partner_id)
        if not partner.exists():
            return self._error('Partner not found', status=404, extra={'partner_id': partner_id})

        return self._success(partner.to_api_dict(include_genres=include_genres))

    # =========================================================
    # GET /api/v1/partners/<id>/genres
    # =========================================================

    @http.route(
        '/api/v1/partners/<int:partner_id>/genres',
        type='http', auth='public', methods=['GET'], csrf=False,
    )
    def get_partner_genres(self, partner_id, **kwargs):
        """
        GET /api/v1/partners/9/genres

        Returns ONLY list of parthers' genres (without other fields).
        """
        partner = request.env[self.MODEL].sudo().browse(partner_id)
        if not partner.exists():
            return self._error('Partner not found', status=404, extra={'partner_id': partner_id})

        return self._success({
            'partner_id': partner.id,
            'partner_name': partner.name,
            'count': len(partner.favorite_genre_ids),
            'genres': [
                {'id': g.id, 'name': g.name}
                for g in partner.favorite_genre_ids
            ],
        })