# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplateReferenceType(models.Model):

    _name = 'product.template.reference.type'
    _description = 'Product Reference Type'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
