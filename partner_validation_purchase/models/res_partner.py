# © 2023 Akretion
# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import Warning as WarningOdoo


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_state = fields.Selection(
        [("new", "New"), ("confirmed", "Confirmed"), ("approved", "Approved")],
        string="Supplier State",
        readonly=True,
        default="new",
        track_visibility="onchange",
    )

    supplier = fields.Boolean(
        string='Supplier',
        compute='_compute_supplier')

    @api.depends('supplier_rank')
    def _compute_supplier(self):
        for record in self:
            record.supplier = True if record.supplier_rank > 0 else False

    def confirm_supplier(self):
        for supplier in self:
            supplier.supplier_state = "confirmed"

    def approve_supplier(self):
        for supplier in self:
            supplier.supplier_state = "approved"

    def reject_supplier(self):
        for supplier in self:
            supplier.supplier_state = "new"

    def write(self, vals):
        if vals.get("supplier_state") == "approved" and self.filtered(
            lambda p: p.supplier and (p.is_company or not p.parent_id)
        ):
            self._check_supplier_state_access()

        if self._should_check_partner_validation():
            self._check_supplier_restricted_fields(vals)

        return super().write(vals)

    def _check_supplier_restricted_fields(self, vals):
        if not self.env.user.has_group(
            "partner_validation_purchase.group_partner_restricted_field_purchases"
        ):
            restricted_fields = (
                self.env["res.partner.restricted.field"]
                .search([("apply_on_purchases", "=", True)])
                .mapped("field_id.name")
            )
            vals_fields = set(vals.keys())
            final_restricted_fields = list(
                set(restricted_fields).intersection(vals_fields)
            )

            restricted_suppliers = self.filtered(
                lambda p: p.supplier
                and p.supplier_state == "approved"
                and (p.is_company or not p.parent_id)
            )
            if final_restricted_fields and restricted_suppliers:
                raise WarningOdoo(
                    _(
                        "You are not authorized to modify the following fields: %s"
                        " when the partner’s status is approved."
                    )
                    % str(final_restricted_fields)
                )

    def _check_supplier_state_access(self):
        if not self.env.user.has_group(
            "partner_validation_purchase.group_partner_restricted_field_purchases"
        ):
            raise WarningOdoo(
                _("Permission to change the state of the partner denied.")
            )
