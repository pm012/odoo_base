from odoo import models, fields

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
