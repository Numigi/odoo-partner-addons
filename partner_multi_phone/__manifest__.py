# -*- coding: utf-8 -*-
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Multi Phone',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'depends': [
        'phone_validation',
        'sms',
    ],
    'data': [
        'views/partner_multi_phone.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
}
