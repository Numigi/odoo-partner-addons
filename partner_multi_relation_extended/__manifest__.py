# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Partner relations - Extended",
    "version": "10.0.1.0.0",
    "author": "Savoir-faire Linux",
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    "complexity": "normal",
    "category": "Customer Relationship Management",
    "license": "LGPL-3",
    "depends": [
        'base_view_inheritance_extension',
        'partner_multi_relation',
        'contacts',
    ],
    'external_dependencies': {
        'python': [],
    },
    'qweb': [],
    "data": [
        'data/res_partner_relation_type.xml',
        'security/ir.model.access.csv',
        'wizards/res_partner_parent_modification.xml',
        'views/res_partner.xml',
        'views/res_partner_relation_all.xml',
        'views/res_partner_relation_type.xml',
        'views/res_partner_relation_strength.xml',
    ],
    "auto_install": False,
    "installable": False,
    'application': False,
}
