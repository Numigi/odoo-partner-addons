# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Validation Sale',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'depends': [
        'partner_validation',
        'sale_stock'
    ],
    'data': [
        'security/res_groups.xml',
        'views/res_partner_restricted_field.xml',
        'views/res_partner.xml'
    ],
    'application': False,
    'installable': True,
}
