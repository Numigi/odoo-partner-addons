# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

INVOICE = "invoice"


class Partner(models.Model):

    _inherit = "res.partner"

    use_parent_invoice_address = fields.Boolean()

    def address_get(self, adr_pref=None):
        res = super().address_get(adr_pref)

        commercial_partner = self.commercial_partner_id

        use_parent_invoice_address = (
            commercial_partner.use_parent_invoice_address
            and commercial_partner.parent_id
        )

        if INVOICE in res and use_parent_invoice_address:
            res[INVOICE] = self.parent_id.address_get([INVOICE])[INVOICE]

        return res

    @api.onchange("parent_id")
    def _update_use_parent_invoice_address(self):
        if not self.parent_id:
            self.use_parent_invoice_address = False
