# © 2023 Akretion
# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import Warning as WarningOdoo


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        if self.env["res.partner"]._should_check_partner_validation():
            self._check_customer_approved_state()
        return super().button_validate()

    def _check_customer_approved_state(self):
        outgoings = self.filtered(
            lambda sp: (
                sp.picking_type_code == "outgoing"
                and sp.location_dest_id.usage == "customer"
            )
        )
        if outgoings:
            restricted_partners = (
                self.mapped("partner_id.commercial_partner_id")
                .filtered(lambda p: p.customer_state != "approved")
                .mapped("display_name")
            )

            if restricted_partners:
                raise WarningOdoo(
                    _(
                        "The partner %s has to be approved in order"
                        " to confirm this stock move."
                    )
                    % (",".join(restricted_partners))
                )
