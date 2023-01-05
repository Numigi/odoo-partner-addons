# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRestrictedField(models.Model):
    _name = 'res.partner.restricted.field'
    _description = 'Partner Restricted Field'

    field_id = fields.Many2one(
        'ir.model.fields', string='Field',
        domain="[('model_id.model', '=', 'res.partner')]", required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('field_id_unique', 'UNIQUE(field_id)', "This field is already restricted")
    ]
