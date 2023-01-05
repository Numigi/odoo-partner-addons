# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Validation',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'depends': [
        'contacts',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/res_partner_restricted_field.xml'
    ],
    'application': False,
    'installable': True,
}
