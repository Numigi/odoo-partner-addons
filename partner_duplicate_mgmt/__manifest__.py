# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Duplicate Management',
    'version': '1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
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
        'data/res_partner_duplicate_field.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/res_partner_duplicate.xml',
        'views/res_partner_duplicate_field.xml',
        'views/merger_reason.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'external_dependencies': {
        'python': ['unidecode'],
    },
    'post_init_hook': 'update_partners_indexed_name',
    'installable': True,
}
