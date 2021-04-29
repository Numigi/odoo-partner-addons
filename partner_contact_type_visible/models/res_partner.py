# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):

    _inherit = "res.partner"

    @api.constrains("type", "parent_id")
    def __check_address_type_versus_parent(self):
        for partner in self:
            if not partner.parent_id and partner.type in ("invoice", "delivery", "other"):
                raise ValidationError(_(
                    "The contact {} has no parent partner. "
                    "Therefore, it can not be typed as invoicing, delivery or other address."
                ).format(partner.display_name))

