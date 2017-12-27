# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplateReference(models.Model):

    _name = 'product.template.reference'
    _description = 'Product Template Reference'

    reference_type_id = fields.Many2one(
        'product.template.reference.type', 'Reference Type')
    value = fields.Char('Value')
    product_id = fields.Many2one('product.template', copy=False)
