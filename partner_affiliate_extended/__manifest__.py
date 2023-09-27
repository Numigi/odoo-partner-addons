# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Affiliate Extended',
    'version': '1.0.2',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Add the field is a parent company to the partner object',
    'depends': ['partner_affiliate', 'mail'],
    'data': [
        'views/res_partner.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
   # "post_init_hook": "post_init_hook",
}
