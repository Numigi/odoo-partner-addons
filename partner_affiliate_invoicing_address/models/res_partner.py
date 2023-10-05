# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

INVOICE = "invoice"


class Partner(models.Model):
    _inherit = "res.partner"

    use_parent_invoice_address = fields.Boolean()
    invoice_address_to_use_id = fields.Many2one(
        "res.partner",
        "Invoice address to use",
        store=True,
        readonly=False,
        domain="['|', '&', ('type', '=', 'invoice') ,('parent_id', '=', parent_id), ('id', '=', parent_id)]",
    )

    @api.onchange("use_parent_invoice_address")
    def _onchange_use_parent_invoice_address(self):
        if not any(child.type == "invoice" for child in self.parent_id.child_ids):
            self.invoice_address_to_use_id = self.parent_id
        else:
            self.invoice_address_to_use_id = False

    def _update_for_specific_invoice_address(self, res={}):
        if res.get(INVOICE, False):
            res[INVOICE] = self.commercial_partner_id.invoice_address_to_use_id.id

    def address_get(self, adr_pref=None):
        res = super().address_get(adr_pref)

        commercial_partner = self.commercial_partner_id

        use_parent_invoice_address = (
            commercial_partner.use_parent_invoice_address
            and commercial_partner.parent_id
        )

        if INVOICE in res and use_parent_invoice_address:
            if not self.commercial_partner_id.invoice_address_to_use_id:
                # this case is only if record still empty
                # even "required" managed on view
                res[INVOICE] = self.parent_id.address_get([INVOICE])[INVOICE]
            else:
                # normally, it shoud only use this case :
                # use_parent_invoice_address set to True,
                # invoice_address_to_use_id shoud not be empty
                self._update_for_specific_invoice_address(res)

        return res

    @api.onchange("parent_id")
    def _update_use_parent_invoice_address(self):
        if not self.parent_id:
            self.use_parent_invoice_address = False
