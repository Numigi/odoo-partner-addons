# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def create(self, vals):
        email = vals.get("email")

        if email and not vals.get("partner_id"):
            partner = self._find_partner_matching_email(email)

            if partner:
                vals = self._get_vals_with_partner_id(vals, partner)

        return super().create(vals)

    @api.model
    def _get_vals_with_partner_id(self, vals, partner):
        if partner and not partner.active:
            raise ValidationError(
                _(
                    "Could not create a user with the email {}. "
                    "The email is linked to an archived partner."
                ).format(partner.email)
            )

        if partner.user_ids:
            raise ValidationError(
                _(
                    "Could not create a user with the email {}. "
                    "The email is linked to an existing partner. "
                    "This partner is already linked to a user account."
                ).format(partner.email)
            )

        partner_vals = partner.read()[0]
        return dict(
            ((k, v) for k, v in vals.items() if k not in partner_vals),
            partner_id=partner.id,
        )

    @api.model
    def _find_partner_matching_email(self, email):
        return (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search([("email", "=", email)], limit=1)
        )
