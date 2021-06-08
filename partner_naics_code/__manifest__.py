# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner NAICS Code",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "AGPL-3",
    "category": "Partner Management",
    "summary": "Adds NAICS code field to contacts and adds a new menu for NAICS code creation.",
    "depends": [
        "contacts",
    ],
    "data": [
        "views/partner_naics.xml",
        "views/res_partner_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
