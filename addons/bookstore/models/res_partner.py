import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    
    _inherit = 'res.partner'  # Extending existig model 
    
    favorite_genre_ids = fields.Many2many(
        'bookstore.genre',
        'res_partner_bookstore_genre_rel',  # unique connections table name
        'partner_id',
        'genre_id',
        string='Favorite Book Genres',
        help='Genres this contact prefers'
    )

# =========================================================
# Constrains
# =========================================================
    @api.constrains('favorite_genre_ids')
    def _check_favorite_genres_limit(self):
        """Less or equal than 5 genres per 1 contact."""
        for partner in self:
            if len(partner.favorite_genre_ids) > 5:
                raise ValidationError(
                    _("Contact '%s' cannot have more than 5 favorite genres. "
                      "Currently: %s")
                    % (partner.name, len(partner.favorite_genre_ids))
                )
# =========================================================
# CRUD overrides (Read, update)
# =========================================================
    @api.model_create_multi
    def create(self, vals_list):
        """
        Extend standard create() using super().

        Odoo logic will staye unchanged, we are adding our own:
        - logging creating of partners with favorite genres
        """
        # 1. Call parent create() — add records
        partners = super().create(vals_list)

        # 2. Custom, additional logic AFTER creation
        for partner in partners:
            if partner.favorite_genre_ids:
                _logger.info(
                    "Bookstore: created partner '%s' (id=%s) with %s favorite genres: %s",
                    partner.name,
                    partner.id,
                    len(partner.favorite_genre_ids),
                    partner.favorite_genre_ids.mapped('name'),
                )

        # 3. Return recordset — mandatory! MANDATORY!!!!!!!!!!!!!!!!!!!!*1000!!!!!!!!!!!!
        return partners


    def write(self, vals):
        """
        Extending write(). Logging genres update.
        """
        # Store old genres before recording
        old_genres = {partner.id: partner.favorite_genre_ids for partner in self}

        # Call parent write()
        result = super().write(vals)

        # Logic AFTER recording - only if genres were in vals
        if 'favorite_genre_ids' in vals:
            for partner in self:
                old = old_genres.get(partner.id, self.env['bookstore.genre'])
                new = partner.favorite_genre_ids
                added = new - old
                removed = old - new
                if added or removed:
                    _logger.info(
                        "Bookstore: partner '%s' (id=%s) genres changed. "
                        "Added: %s. Removed: %s",
                        partner.name, partner.id,
                        added.mapped('name'), removed.mapped('name'),
                    )

        return result

    # =========================================================
    # API: serialization
    # =========================================================

    def to_api_dict(self, include_genres=True):
        """
        Serialization of partner for API.

        :param include_genres: bool — to define if list of genreshould be included
        :return: dict
        """
        self.ensure_one()
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email or None,
            'phone': self.phone or None,
            'is_company': self.is_company,
            'city': self.city or None,
            'country': self.country_id.name if self.country_id else None,
        }
        if include_genres:
            data['favorite_genres'] = [
                {'id': g.id, 'name': g.name}
                for g in self.favorite_genre_ids
            ]
        return data

    # =========================================================
    # API: read
    # =========================================================

    @api.model
    def get_partners_data(self, limit=None, offset=0, genre_id=None, include_genres=True):
        """
        List of partners for API.

        :param limit: int|None — maximum of records
        :param offset: int — shift(offset)
        :param genre_id: int|None — filter by favorite genre
        :param include_genres: bool — if genres shuld be included?
        :return: dict {'count': int, 'limit': ..., 'offset': ..., 'partners': [...]}
        """
        domain = []
        if genre_id:
            domain.append(('favorite_genre_ids', 'in', genre_id))

        partners = self.search(domain, limit=limit, offset=offset)
        return {
            'count': self.search_count(domain),
            'limit': limit,
            'offset': offset,
            'genre_id': genre_id,
            'partners': [p.to_api_dict(include_genres=include_genres) for p in partners],
        }