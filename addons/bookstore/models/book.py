from odoo import models, fields, api

class BookstoreBook(models.Model):
    _name = 'bookstore.book'
    _description = 'Bookstore Book'

    name = fields.Char(string='Title', required=True)
    author_id = fields.Many2one('bookstore.author', string='Author', ondelete='restrict')
    description = fields.Html(string='Description')
    price = fields.Float(string='Price', default=0.0)
    isbn = fields.Char(string='ISBN')
    active = fields.Boolean(string='Active', default=True)
    quantity = fields.Integer(string='Quantity', default=0)
    total_value = fields.Float(
        string='Total Value', 
        compute='_compute_total_value', 
        store=True
    )

    genre_ids = fields.Many2many(
    comodel_name='bookstore.genre',
    relation='bookstore_book_genre_rel',  # the same name as in genre.py!!!
    column1='book_id',                    # curent model here — book
    column2='genre_id',
    string='Genres',
)

    @api.depends('price', 'quantity')
    def _compute_total_value(self):
        for book in self:
            book.total_value = book.price * book.quantity
