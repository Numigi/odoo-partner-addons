# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ResPartner(models.Model):

    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']

    @api.onchange('phone', 'country_id', 'company_id')
    def _onchange_phone_validation(self):
        if self.phone:
            self.phone = self.phone_format(self.phone)

    @api.onchange('mobile', 'country_id', 'company_id')
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self.phone_format(self.mobile)

    @api.model
    def _get_phone_fields(self):
        return ['phone', 'mobile']

    def _apply_phone_format_to_saved_vals(self, vals):
        formatted_phones = {}
        for field in self._get_phone_fields():
            if vals.get(field):
                formatted_phones[field] = self.phone_format(vals[field])

        phones_to_update = {
            k: v for k, v in formatted_phones.items()
            if vals[k] != v
        }

        if phones_to_update:
            self.with_context(no_partner_format_phones=True).write(phones_to_update)

    def write(self, vals):
        res = super().write(vals)

        if not self._context.get('no_partner_format_phones'):
            for partner in self:
                partner._apply_phone_format_to_saved_vals(vals)

        return res

    @api.model
    def create(self, vals):
        partner = super().create(vals)
        partner._apply_phone_format_to_saved_vals(vals)
        return partner
