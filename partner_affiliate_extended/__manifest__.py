# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Affiliate Extended',
    'version': '1.0.4',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Add the field is a parent company to the partner object',
    'depends': ['partner_affiliate', 'contacts'],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
}
