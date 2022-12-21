# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Name No Shortcut',
    'version': '1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Automatically Remove Shortcuts From Partner Names.',
    'depends': ['contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_business_type.xml',
    ],
    'installable': True,
}
