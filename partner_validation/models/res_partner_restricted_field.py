# -*- coding: utf-8 -*-
# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class ResPartnerRestrictedField(models.Model):
    _name = 'res.partner.restricted.field'
    _description = 'Partner Restricted Field'

    @api.model
    def _get_model_domain(self):
        partner_model_id = self.env.ref('base.model_res_partner').id
        return "[('model_id', '=', %s)]" % partner_model_id

    field_id = fields.Many2one(
        'ir.model.fields', string='Field',
        domain=_get_model_domain, required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('field_id_unique', 'UNIQUE(field_id)', "This field is already restricted")
    ]
