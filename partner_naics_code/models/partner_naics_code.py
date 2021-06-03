# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PartnerNaicsCode(models.Model):
    _name = "partner.naics.code"
    _description = "Partner NAICS Code"

    name = fields.Char(invisible=True, compute="_compute_name", store=True)
    code = fields.Integer(string="NAICS Code", required=True)
    class_title = fields.Char(string="Class Title", required=True)

    @api.one
    @api.constrains("code")
    def _check_value(self):
        if self.code < 0:
            raise ValidationError(_("Please enter a positive value."))

    @api.depends('code','class_title')   
    def _compute_name(self):
        for rec in self:
            rec.name = "{} - {}".format(rec.code, rec.class_title)
