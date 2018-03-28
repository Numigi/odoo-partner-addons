# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Google Partner Address',
    'version': '1.0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Add address assisted selection',
    'depends': [
        'base_setup',
        'web_enterprise',
    ],
    'data': [
        'views/base_config_settings.xml',
        'views/res_partner.xml',
    ],
    'qweb': [
        'static/src/xml/google_partner_address.xml',
    ],
    'installable': True,
}
