# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Multi Phone',
    'version': '1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'depends': [
        'base_view_inheritance_extension',
        'partner_phone_validation',
        'sms',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
}
