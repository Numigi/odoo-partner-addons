# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Full Text Search",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "AGPL-3",
    "category": "Partner Management",
    "summary": "Add full text search to partners",
    "depends": [
        "base_search_fuzzy",
    ],
    "data": [
        "data/trgm_index.xml",
        "views/res_partner.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
