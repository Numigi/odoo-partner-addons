# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Duplicate Management',
    'version': '10.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'summary': 'Manage Partner Duplicates',
    'depends': [
        'contacts',
        'crm',
        'mail',
        'account',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'data/merger_reason.xml',
        'data/res_partner.xml',
        'demo/res_partner_duplicate_field.xml',
        'demo/res_partner_duplicate_term.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/res_partner_duplicate.xml',
        'views/res_partner_duplicate_field.xml',
        'views/res_partner_duplicate_term.xml',
        'views/merger_reason.xml',
    ],
    'external_dependencies': {
        'python': ['unidecode'],
    },
    'post_init_hook': 'update_partners_indexed_name',
    'installable': True,
    'application': True,
}
