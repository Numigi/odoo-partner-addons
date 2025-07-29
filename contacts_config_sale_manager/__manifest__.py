# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Contacts Configuration Sale Manager',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://numigi.com/r/home',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Add the menu Contacts / Configuration to sale managers',
    'depends': [
        'contacts',
        'sales_team',
    ],
    'data': [
        'views/menu.xml',
    ],
    'installable': True,
}
