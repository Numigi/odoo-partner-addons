# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Tracking',
    'version': '1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Extra Rights',
    'depends': [
        'account',
    ],
    'data': [
        'security/res_groups.xml',
        'views/res_partner.xml',
    ],
    'application': False,
    'installable': False,
}
