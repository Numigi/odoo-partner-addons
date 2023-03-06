# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ForwardSortationAera(models.Model):
    _inherit = "forward.sortation.area"

    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.user.company_id
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name, company_id)",
            "FSA name must be unique per company!",
        ),
    ]

    @api.one
    @api.constrains("territory_ids", "company_id")
    def _check_territory_ids(self):
        if any(f.company_id != self.company_id for f in self.territory_ids):
            raise ValidationError(
                _("The FSA and Territory must belong to the same company (%s).")
                % self.company_id.name
            )
