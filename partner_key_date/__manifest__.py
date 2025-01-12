# -*- coding: utf-8 -*-
# Copyright 2017 Savoir-faire Linux
# Copyright 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partner Key Dates",
    "version": "1.1.0",
    "author": "Savoir-faire Linux",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Partner Management",
    "depends": ["mail", "contacts"],
    "data": [
        "data/email_template.xml",
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/res_partner_date_views.xml",
        "views/res_partner_date_type_views.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ["freezegun"],
    },
}
