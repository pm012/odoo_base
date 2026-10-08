from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class BookstoreAuthor(models.Model):
    _name = 'bookstore.author'
    _description = 'Bookstore Author'

    name = fields.Char(string='Name', required=True)
    biography = fields.Text(string='Biography')
    birth_date = fields.Date(string='Birth Date')

    book_ids = fields.One2many(
        comodel_name='bookstore.book',
        inverse_name='author_id',
        string='Books'
        )

    @api.constrains('birth_date')
    def _check_birth_date(self):
        for author in self:
            if author.birth_date and author.birth_date > fields.Date.context_today(self): 
                #Note!!! fields.Date.today() - current date in UTC, while fields.Date.context_today(self) - current date in user's timezone
                raise ValidationError(_('Birth date cannot be in the future. Author: %s')  % author.name)