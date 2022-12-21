# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Website Sale No VAT',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'license': 'LGPL-3',
    'category': 'Other',
    'summary': 'Hide VAT on ecommerce checkout address',
    'depends': [
        'website_sale',
        'partner_no_vat'
    ],
    'data': [
        'views/checkout_address.xml',
    ],
    'installable': True,
    'auto_install': True,
}
