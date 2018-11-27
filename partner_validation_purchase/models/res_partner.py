# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import Warning as WarningOdoo


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_state = fields.Selection(
        [('new', 'New'), ('confirmed', 'Confirmed'), ('approved', 'Approved')],
        string='Supplier State', readonly=True, default='new', track_visibility='onchange')

    def check_supplier_state_access(self):
        if not self.env.user.has_group('partner_validation_purchase.group_partner_restricted_field_purchases'):
            raise WarningOdoo(_("Permission to change the state of the partner denied."))

    @api.multi
    def confirm_supplier(self):
        for supplier in self:
            supplier.supplier_state = 'confirmed'

    @api.multi
    def approve_supplier(self):
        for supplier in self:
            supplier.supplier_state = 'approved'

    @api.multi
    def reject_supplier(self):
        for supplier in self:
            supplier.supplier_state = 'new'

    @api.multi
    def write(self, vals):
        if vals.get('supplier_state') == 'approved' and \
                self.filtered(lambda p: p.supplier and (p.is_company or not p.parent_id)):
            self.check_supplier_state_access()
        if not self.env.user.has_group('partner_validation_purchase.group_partner_restricted_field_purchases'):
            restricted_fields = self.env['res.partner.restricted.field']. \
                search([('apply_on_purchases', '=', True)]).mapped('field_id.name')
            vals_fields = set(vals.keys())
            final_restricted_fields = list(set(restricted_fields).intersection(vals_fields))

            restricted_suppliers = self.filtered(lambda p: p.supplier and p.supplier_state == 'approved'
                                                 and (p.is_company or not p.parent_id))
            if final_restricted_fields and restricted_suppliers:
                raise WarningOdoo(_("You are not authorized to modify the following fields: %s"
                                    " when the partner’s status is approved" % str(final_restricted_fields)))

        return super(ResPartner, self).write(vals)
