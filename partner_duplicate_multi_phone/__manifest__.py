# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Duplicate with Phone Numbers',
    'version': '10.0.1.0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Find duplicates using phone numbers.',
    'depends': [
        'partner_duplicate_mgmt',
        'partner_multi_phone',
    ],
    'data': [
        'views/res_partner_duplicate.xml',
    ],
    'installable': True,
    'application': False,
}
