# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partner Multi Relation Strength",
    "version": "1.0.0",
    "author": "Savoir-faire Linux",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "category": "Customer Relationship Management",
    "license": "LGPL-3",
    "depends": [
        "partner_multi_relation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_relation_strength.xml",
        "views/res_partner_relation_all.xml",
        "views/res_partner_relation_strength.xml",
    ],
    "installable": True,
}
