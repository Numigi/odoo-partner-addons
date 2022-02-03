# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from datetime import date

_logger = logging.getLogger(__name__)


class ResPartnerDate(models.Model):

    _name = 'res.partner.date'
    _description = 'Contact Key Date'

    date_type_id = fields.Many2one(
        'res.partner.date.type', string='Date Type', required=True, index=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, ondelete='cascade')
    date = fields.Date('Date', required=True, index=True)
    note = fields.Char('Note')
    age = fields.Float('Age', digits=(16, 1), index=True)

    month_and_day = fields.Char(
        'Month and Day', compute='_compute_month_and_day', index=True, store=True)
    diffusion = fields.Boolean(
        'Diffusion',
        help='If the box is checked, an email will be sent to the contact at '
             'every anniversary of the this date.')

    def compute_age_for_all_dates(self):
        """Compute the age of all partner dates.

        The age of a date is in years.

        We use the the system time zone, whatever it is.
        The difference between time zones is not significant to make a difference
        in the year of a date.
        """
        self.env.cr.execute("""
            UPDATE res_partner_date
            SET age = round((%s - date) / 365.25, 1)
            """, (date.today(),))

    def _compute_age(self):
        """Compute the age of a single date."""
        key_date = fields.Date.from_string(self.date)
        today = date.today()
        self.age = round((today - key_date).days / 365.25, 1)

    @api.depends('date')
    def _compute_month_and_day(self):
        for record in self:
            key_date = fields.Date.from_string(record.date)
            record.month_and_day = key_date.strftime('%m-%d')

    @api.constrains('diffusion', 'date_type_id')
    def _check_mail_template_is_defined_on_date_type_if_diffusion_is_checked(self):
        dates_with_diffusion_and_no_template = self.filtered(
            lambda d: d.diffusion and not d.date_type_id.mail_template_id)
        if dates_with_diffusion_and_no_template:
            raise UserError(_(
                'The diffusion may not be checked for this partner date ({date_type}), '
                'because there is no mail template defined on this date type.'
            ).format(date_type=dates_with_diffusion_and_no_template[0].date_type_id.display_name))

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._compute_age()
        return res

    @api.multi
    def write(self, vals):
        super().write(vals)
        if 'date' in vals:
            for record in self:
                record._compute_age()
        return True

    @api.model
    def send_anniversary_emails(self):
        for key_date in self._find_anniversary_dates():
            key_date._send_anniversary_emails()
        return True

    def _send_anniversary_emails(self):
        if not self.partner_id.email:
            _logger.error(
                'The email for the anniversary of {date_type} could not be sent '
                'to {partner} because this partner has no email.'
                .format(
                    date_type=self.date_type_id.display_name,
                    partner=self.partner_id.display_name,
                ))
            return

        mail_template = self.date_type_id.mail_template_id
        if not mail_template:
            _logger.error(
                'The email for the anniversary of {date_type} could not be sent '
                'to {partner} because no mail template is defined on the date type.'
                .format(
                    date_type=self.date_type_id.display_name,
                    partner=self.partner_id.display_name,
                ))
            return

        mail_template.write({
            'email_from': self.env.user.email,
            'email_to': self.partner_id.email,
        })
        mail_template.send_mail(self.id)

    @api.model
    def _find_anniversary_dates(self):
        res = self.browse([])

        date_types = self.env["res.partner.date.type"].search([])
        for type_ in date_types:
            res |= type_._find_anniversary_dates()

        return res
