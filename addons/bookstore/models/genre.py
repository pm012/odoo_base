from odoo import models, fields

class BookstoreGenre(models.Model):
    _name = 'bookstore.genre'
    _description = 'Book Genre'

    name = fields.Char(string='Genre Name', required=True)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Color Index')  # for attractive display in tags

    book_ids = fields.Many2many(
        comodel_name='bookstore.book',
        relation='bookstore_book_genre_rel',  # name of the intermediate table
        column1='genre_id',                   # FK on this model (genre)
        column2='book_id',                    # FK on book
        string='Books',
    )