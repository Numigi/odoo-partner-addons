# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Reference',
    'version': '10.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Add new field references to res.partner',
    'depends': [
        'sales_team',
    ],
    'data': [
        'views/res_partner.xml',
        'views/res_partner_reference_type.xml',
    ],
    'installable': True,
    'application': False,
}
