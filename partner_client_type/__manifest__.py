# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partner Client Type",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Partner Management",
    "depends": ["mail", "contacts", "base", "sales_team"],
    "data": [
        "views/client_type.xml",
        "views/res_partner_views.xml",
        "views/contact_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
