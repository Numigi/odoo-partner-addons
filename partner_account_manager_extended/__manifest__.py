# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Account Manager Extended",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Other",
    "depends": ["partner_account_manager", "sale"],
    "summary": "Adds the account manager field available on some view and options.",
    "data": [
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
