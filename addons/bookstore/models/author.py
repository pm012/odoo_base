from odoo import models, fields

class BookstoreAuthor(models.Model):
    _name = 'bookstore.author'
    _description = 'Bookstore Author'

    name = fields.Char(string='Name', required=True)
    biography = fields.Text(string='Biography')
    birth_date = fields.Date(string='Birth Date')
