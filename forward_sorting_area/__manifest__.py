# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Forward Sorting Areas",
    "version": "1.1.0",
    "author": "Savoir-faire Linux",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Partner Management",
    "summary": "Add territories and forward sorting areas (FSA)",
    "depends": [
        "base_setup",
        "contacts",
        "web_list_column_width",
        "mail_improved_tracking_value",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/forward_sortation_area.xml",
        "views/res_partner.xml",
        "views/res_territory.xml",
    ],
    "installable": True,
}
