from odoo import models, fields, api

class BookstoreBook(models.Model):
    _name = 'bookstore.book'
    _description = 'Bookstore Book'

    name = fields.Char(string='Title', required=True)
    author_id = fields.Many2one('bookstore.author', string='Author')
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

    @api.depends('price', 'quantity')
    def _compute_total_value(self):
        for book in self:
            book.total_value = book.price * book.quantity
