# © 2023 Akretion
# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, _
from odoo.exceptions import Warning as WarningOdoo


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        if self.env["res.partner"]._should_check_partner_validation():
            self._check_customer_approved_state()
        return super().action_confirm()

    def _check_customer_approved_state(self):
        restricted_partners = (
            self.mapped("partner_id.commercial_partner_id")
            .filtered(lambda p: p.customer_state != "approved")
            .mapped("display_name")
        )
        if restricted_partners:
            raise WarningOdoo(
                _(
                    "The client ​%s has to be approved"
                    " in order to confirm this sale order."
                )
                % (",".join(restricted_partners))
            )
