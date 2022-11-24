# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


PARTNER_WITH_SAME_EMAIL_MESSAGE = _(
    "The email ({email}) entered for {partner} is identical to the email "
    "of another partner ({other_partner})."
)


class ResPartnerWithUniqueEmail(models.Model):
    """Prevent duplicate emails on partners."""

    _inherit = 'res.partner'

    email = fields.Char(copy=False)

    @api.onchange('email')
    def _onchange_email_check_partners_with_same_email(self):
        if self.email:
            partner_with_same_email = self._find_partner_with_same_email()
            if partner_with_same_email:
                raise UserError(_(PARTNER_WITH_SAME_EMAIL_MESSAGE).format(
                    partner=self.display_name,
                    other_partner=partner_with_same_email.display_name,
                    email=self.email,
                ))

    @api.constrains('email')
    def _check_duplicate_emails(self):
        partners_with_emails = self.filtered(lambda p: p.email)

        for partner in partners_with_emails:
            partner_with_same_email = self._find_partner_with_same_email()
            if partner_with_same_email:
                raise ValidationError(_(PARTNER_WITH_SAME_EMAIL_MESSAGE).format(
                    partner=partner.display_name,
                    other_partner=partner_with_same_email.display_name,
                    email=partner.email,
                ))

    def _find_partner_with_same_email(self):
        """Find a single partner with the same email.

        :return: a res.partner record
        """
        domain = [('email', '=', self.email)]

        if not isinstance(self.id, models.NewId):
            domain.append(('id', '!=', self.id))

        return (
            self.env['res.partner']
            .sudo()  # Prevent access rules from interfering with the constraint.
            .with_context(active_test=False)  # Find duplicate emails in archived partners as well.
            .search(domain, limit=1)
        )
