# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerReference(models.Model):

    _name = 'res.partner.reference'
    _description = 'Partner Reference'

    reference_type_id = fields.Many2one(
        'res.partner.reference.type', 'Reference Type')
    value = fields.Char('Value')
    partner_id = fields.Many2one('res.partner', copy=False)
