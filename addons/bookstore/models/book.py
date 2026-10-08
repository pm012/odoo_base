import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

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
    # NB!!!!! api.constrains - server validation; api.onchange - client validation (in the form view, before saving the record)
    @api.constrains('price', 'quantity')
    def _check_price_quantity(self):
        for book in self:
            if book.price < 0:
                # raise ValidationError(_('Price cannot be negative. Book: %s, Price: %s') % (book.name, book.price))
                raise ValidationError(self.env._("Price cannot be negative.\nBook: %s\nPrice: %s") % (book.name, book.price)) # self.env is considered better practice than using _() directly for translations in Odoo
            if book.quantity < 0:
                raise ValidationError(_('Quantity cannot be negative. Book: %s, Quantity: %s') % (book.name, book.quantity))

    # Verify that the ISBN is either a valid ISBN-10 or ISBN-13 format
    @api.constrains('isbn')
    def _check_isbn(self):
        for book in self:
            if not book.isbn:
                continue  # Skip validation if ISBN is empty

            # Remove any hyphens or spaces from the ISBN
            isbn_cleaned = re.sub(r'[-\s]', '', book.isbn)
            # ISBN-10 10 symbols (last symbol can be X) or ISBN-13 13 digits
            if not re.match(r'^(?:\d{9}[\dX]|\d{13})$', isbn_cleaned):
                raise ValidationError(_('Invalid ISBN format: %s. Must be ISBN-10 or ISBN-13') % book.isbn)