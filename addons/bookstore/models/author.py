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
        string='Books',
    )

    # =========================================================
    # Constrains
    # =========================================================

    @api.constrains('birth_date')
    def _check_birth_date(self):
        today = fields.Date.context_today(self)
        for author in self:
            if author.birth_date and author.birth_date > today:
                raise ValidationError(
                    _("Birth date cannot be in the future. Author: %s") % author.name
                )

    # =========================================================
    # API: serialization
    # =========================================================

    def to_api_dict(self, include_books=False):
        """
        Serialisation of one author for API.
        

        :param include_books: bool — should we include list of books
        :return: dict
        """
        self.ensure_one()
        data = {
            'id': self.id,
            'name': self.name,
            'biography': self.biography or '',
            'birth_date': str(self.birth_date) if self.birth_date else None,
            'book_count': len(self.book_ids),
        }
        if include_books:
            data['books'] = [
                {
                    'id': b.id,
                    'name': b.name,
                    'price': b.price,
                    'quantity': b.quantity,
                }
                for b in self.book_ids
            ]
        return data

    # =========================================================
    # API: read
    # =========================================================

    @api.model
    def get_authors_data(self, limit=None, offset=0, domain=None, include_books=False):
        """
        List of authors for API.

        :param limit: int|None — maximum of records
        :param offset: int — offset
        :param domain: list — Odoo-domain for filtering
        :param include_books: bool — should we include books
        :return: dict {'count': int, 'limit': ..., 'offset': ..., 'authors': [...]}
        """
        domain = domain or []
        authors = self.search(domain, limit=limit, offset=offset)
        total = self.search_count(domain)
        return {
            'count': total,
            'limit': limit,
            'offset': offset,
            'authors': [a.to_api_dict(include_books=include_books) for a in authors],
        }

    # =========================================================
    # API: create
    # =========================================================

    @api.model
    def create_from_api(self, payload):
        """
        Create author from API-query.
        
        :param payload: dict
        :return: dict — serialized author
        :raises ValueError: if validation failed
        """
        if not isinstance(payload, dict):
            raise ValueError('Payload must be a dict')

        name = payload.get('name')
        if not name or not str(name).strip():
            raise ValueError('Field "name" is required')

        vals = {
            'name': str(name).strip(),
            'biography': payload.get('biography', ''),
            'birth_date': payload.get('birth_date'),  # 'YYYY-MM-DD' or None
        }

        try:
            author = self.create(vals)
        except ValidationError as e:
            raise ValueError(str(e))

        return author.to_api_dict()

    # =========================================================
    # API: update
    # =========================================================

    def write_from_api(self, payload):
        """
        Update author from API -query.

        :param payload: dict
        :raises ValueError: if validation did not pass
        """
        self.ensure_one()
        if not isinstance(payload, dict):
            raise ValueError('Payload must be a dict')

        allowed = {'name', 'biography', 'birth_date'}
        vals = {k: v for k, v in payload.items() if k in allowed}

        if not vals:
            raise ValueError(f'No valid fields to update. Allowed: {sorted(allowed)}')

        if 'name' in vals and (not vals['name'] or not str(vals['name']).strip()):
            raise ValueError('Field "name" cannot be empty')
        if 'name' in vals:
            vals['name'] = str(vals['name']).strip()

        try:
            self.write(vals)
        except ValidationError as e:
            raise ValueError(str(e))