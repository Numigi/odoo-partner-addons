# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Firstname Before Lastname',
    'version': '1.0.1',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Display the firstname before the lastname on partner forms.',
    'depends': ['partner_firstname'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
}
