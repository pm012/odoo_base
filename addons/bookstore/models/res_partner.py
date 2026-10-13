from odoo import models, fields

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