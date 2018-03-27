# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Partner Multi Relation Work",
    "version": "11.0.1.0.0",
    "author": "Savoir-faire Linux",
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    "complexity": "normal",
    "category": "Customer Relationship Management",
    "license": "LGPL-3",
    "depends": [
        'base_view_inheritance_extension',
        'partner_multi_relation',
        'contacts',
    ],
    "data": [
        'data/res_partner_relation_type.xml',
        'wizards/res_partner_parent_modification.xml',
        'views/res_partner.xml',
    ],
    "installable": True,
}
