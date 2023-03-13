# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partner Client Type",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Partner Management",
    "depends": ["mail", "contacts", "base", "sales_team"],
    "data": [
        "views/client_type.xml",
        "views/res_partner.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
