# © 2023 Akretion
# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import Warning as WarningOdoo


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_state = fields.Selection(
        [("new", "New"), ("confirmed", "Confirmed"), ("approved", "Approved")],
        string="Customer State",
        readonly=True,
        default="new",
        track_visibility="onchange",
    )
    customer = fields.Boolean(
        string='Customer',
        compute='_compute_customer')

    @api.depends('customer_rank')
    def _compute_customer(self):
        for record in self:
            record.customer = True if record.customer_rank > 0 else False

    def confirm_customer(self):
        for customer in self:
            customer.customer_state = "confirmed"

    def approve_customer(self):
        for customer in self:
            customer.customer_state = "approved"

    def reject_customer(self):
        for customer in self:
            customer.customer_state = "new"

    def write(self, vals):
        if vals.get("customer_state") == "approved" and self.filtered(
            lambda p: p.customer and (p.is_company or not p.parent_id)
        ):
            self._check_customer_state_access()

        if self._should_check_partner_validation():
            self._check_customer_restricted_fields(vals)

        return super().write(vals)

    def _check_customer_state_access(self):
        if not self.env.user.has_group(
            "partner_validation_sale.group_partner_restricted_field_sales"
        ):
            raise WarningOdoo(
                _("Permission to change the state of the partner denied.")
            )

    def _check_customer_restricted_fields(self, vals):
        if not self.env.user.has_group(
            "partner_validation_sale.group_partner_restricted_field_sales"
        ):
            restricted_fields = (
                self.env["res.partner.restricted.field"]
                .search([("apply_on_sales", "=", True)])
                .mapped("field_id.name")
            )
            vals_fields = set(vals.keys())
            final_restricted_fields = list(
                set(restricted_fields).intersection(vals_fields)
            )

            restricted_customers = self.filtered(
                lambda p: p.customer
                and p.customer_state == "approved"
                and (p.is_company or not p.parent_id)
            )
            if final_restricted_fields and restricted_customers:
                raise WarningOdoo(
                    _(
                        "You are not authorized to modify the following fields: %s"
                        " when the partner’s status is approved."
                    )
                    % str(final_restricted_fields)
                )
