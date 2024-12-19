# Copyright 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.addons.phone_validation.tools import phone_validation


class ResPartner(models.Model):

    _name = "res.partner"
    _inherit = ["res.partner"]

    @api.onchange("phone", "country_id", "company_id")
    def _onchange_phone_validation(self):
        if self.phone:
            self.phone = self._phone_format(self.phone, force_format="INTERNATIONAL")

    @api.onchange("mobile", "country_id", "company_id")
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self._phone_format(self.mobile, force_format="INTERNATIONAL")

    def _phone_format(self, number, country=None, company=None, force_format="E164"):
        country = country or self.country_id or self.env.company.country_id
        if not country or not number:
            return number
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format=force_format,
            raise_exception=False,
        )

    def _phone_get_number_fields(self):
        return ["mobile", "phone"]

    def _apply_phone_format_to_saved_vals(self, vals):
        formatted_phones = {}
        for field in self._phone_get_number_fields():
            if vals.get(field):
                formatted_phones[field] = self._phone_format(
                    vals[field], force_format="INTERNATIONAL"
                )

        phones_to_update = {k: v for k, v in formatted_phones.items() if vals[k] != v}

        if phones_to_update:
            self.with_context(no_partner_format_phones=True).write(phones_to_update)

    def write(self, vals):
        res = super().write(vals)

        if not self._context.get("no_partner_format_phones"):
            for partner in self:
                partner._apply_phone_format_to_saved_vals(vals)

        return res

    @api.model
    def create(self, vals):
        partner = super().create(vals)
        partner._apply_phone_format_to_saved_vals(vals)
        return partner
