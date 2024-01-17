# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Category Type',
    'version': '1.0.2',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Seperate the partner tags into 4 different fields.',
    'depends': ['base'],
    'data': [
        'views/res_partner.xml',
        'views/res_partner_category.xml',
    ],
    'installable': True,
}
