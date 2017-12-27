# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    reference_ids = fields.One2many(
        'product.template.reference', 'product_id', copy=False)
