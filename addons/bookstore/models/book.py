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

    # Non-stored - for "live" calculations, not saved in the database
    total_value_display = fields.Float(
        string='Total Value (Display)',
        compute='_compute_total_value',
        store=False
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
    
    @api.depends('price', 'quantity')
    def _compute_total_value_display(self):
        for book in self:
            book.total_value_display = book.price * book.quantity
    
    # NB!!!!! api.constrains - server validation; api.onchange - client validation (in the form view, before saving the record)
    @api.constrains('price', 'quantity')
    def _check_price_quantity(self):
        for book in self:
            if book.price < 0:
                # raise ValidationError(_('Price cannot be negative. Book: %s, Price: %s') % (book.name, book.price))
                raise ValidationError(self.env._("Price cannot be negative.\nBook: %s\nPrice: %s") % (book.name, book.price)) # self.env is considered better practice than using _() directly for translations in Odoo
            if book.quantity < 0:
                raise ValidationError(self.env._("Quantity cannot be negative.\nBook: %s\nQuantity: %s") % (book.name, book.quantity))

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

    # Onchange frontend triger for price and quantity fields to ensure they are non-negative before saving
    @api.onchange('genre_ids')
    def _onchange_genre_ids(self):
        if len(self.genre_ids) > 3:
            return {
                'warning': {
                    'title': _("Note"),
                    'message': _("This book has %s genres. "
                                "More than 3 may confuse readers, "
                                "but you can still save.")
                            % len(self.genre_ids),
                }
            }

    @api.onchange('author_id')
    def _onchange_author_id(self):
        if self.author_id and not self.price:
            other_books = self.author_id.book_ids.filtered(
                lambda b: b.id != self.id
            )
            if other_books:
                avg_price = sum(other_books.mapped('price')) / len(other_books)
                self.price = round(avg_price, 2)
                return {
                    'warning': {
                        'title': _("Price Suggested"),
                        'message': _("Average price for this author's books: %s")
                                   % round(avg_price, 2),
                    }
                }
