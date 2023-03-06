# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResTerritory(models.Model):
    _inherit = "res.territory"

    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.user.company_id
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name, company_id)",
            "Territory name must be unique per company!",
        ),
    ]

    @api.one
    @api.constrains("fsa_ids", "company_id")
    def _check_fsa_ids(self):
        if any(t.company_id != self.company_id for t in self.fsa_ids):
            raise ValidationError(
                _("The FSA and Territory must belong to the same company (%s)."
                  )
                % self.company_id.name
            )
