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