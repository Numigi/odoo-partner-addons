# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PartnerNaicsCode(models.Model):
    _name = "partner.naics.code"
    _description = "Partner NAICS Code"

    code = fields.Integer(string="NAICS Code", required=True)
    class_title = fields.Char(string="Class Title", required=True)

    @api.one
    @api.constrains("code")
    def _check_value(self):
        if self.code < 0:
            raise ValidationError(_("Please enter a positive value."))

    @api.multi
    def name_get(self):
        return [(rec.id, "%s - %s" % (rec.code, rec.class_title)) for rec in self]
