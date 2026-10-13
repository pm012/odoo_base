{
    'name': 'Bookstore Management',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Module for managing books and authors',
    'author': 'Kroshka & Co',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/book_views.xml',
        'views/genre_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}