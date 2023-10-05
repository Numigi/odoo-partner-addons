# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Partner Affiliate Invoice Address",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "category": "Other",
    "summary": "Use the invoicing address from the parent commercial partner for ecommerce",
    "depends": [
        "website_sale_invoice_address",
        "partner_affiliate_invoicing_address",
    ],
    "data": [
        "views/website_sale_payment_templates.xml",
        "views/website_sale_checkout_templates.xml"
    ],
    "installable": True,
}
