# © 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerBirthCity(models.Model):

    _name = 'res.partner.birth.city'
    _description = 'City of birth'

    code = fields.Char(string="Code", required=1)
    name = fields.Char(string="Birth City", required=1)
    active = fields.Boolean(string="Active", default=True)

    @api.multi
    @api.constrains('code')
    def _check_code(self):
        """Check code."""
        for rec in self:
            if not rec.code.isalpha():
                raise ValidationError(_("The city code should be alpha"))

    @api.multi
    def name_get(self):
        """Get Complete name of a birth city.

        :return: List of tuples of  (code)
        """
        result = []
        for record in self:
            code = '%s ' % (record.code)
            result.append((record.id, code))
        return result
