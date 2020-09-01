# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner No VAT',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'license': 'LGPL-3',
    'category': 'Other',
    'summary': 'Hide VAT on partners',
    'depends': [
        'portal',
    ],
    'data': [
        'views/portal.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
}
