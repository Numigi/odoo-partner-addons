# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partner Key Dates",
    "version": "18.0.1.1.0",
    "author": "Savoir-faire Linux",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Partner Management",
    "depends": ["mail", "contacts"],
    "data": [
        "data/email_template.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/res_partner_date.xml",
        "views/res_partner_date_type.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ["freezegun"],
    },
}
