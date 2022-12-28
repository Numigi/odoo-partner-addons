# © 2017 Savoir-faire Linux
# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Partner Change Parent",
    "version": "1.1.0",
    "author": "Savoir-faire Linux",
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    "complexity": "normal",
    "category": "Customer Relationship Management",
    "license": "LGPL-3",
    "depends": [
        'base_view_inheritance_extension',
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/res_partner_change_parent.xml',
        'views/res_partner.xml',
    ],
    "installable": True,
}
