# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from datetime import date


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


class ResPartnerDateWithAnniversaryEmails(models.Model):
    """Allow sending emails at the anniversary of a key date."""

    _inherit = 'res.partner.date'

    month_and_day = fields.Char(
        'Month and Day', compute='_compute_month_and_day', index=True, store=True)
    diffusion = fields.Boolean(
        'Diffusion',
        help='If the box is checked, an email will be sent to the contact at '
             'every anniversary of the this date.')

    @api.depends('date')
    def _compute_month_and_day(self):
        for record in self:
            key_date = fields.Date.from_string(record.date)
            record.month_and_day = key_date.strftime('%m-%d')

    @api.model
    def send_anniversary_emails(self):
        """Send anniversary emails."""
        for key_date in self._find_anniversary_dates():
            if not key_date.partner_id.email:
                raise UserError(
                    _('The email for the anniversary of {date_type} could not be sent '
                      'to {partner} because this partner has no email.')
                    .format(
                        date_type=key_date.date_type_id.display_name,
                        partner=key_date.partner_id.display_name,
                    ))

            email_template = self.env.ref('partner_key_date.anniversary_email_template')
            email_template.write({
                'email_from': self.env.user.email,
                'email_to': key_date.partner_id.email,
            })
            email_template.send_mail(key_date.id)

        return True

    @api.model
    def _find_anniversary_dates(self):
        """Find anniversary dates.

        This method is used to find dates for which the anniversary is today.

        The time zone of the user is used to select dates.
        Otherwise, if the function is called at 20h00 in Canada, and the system timezone is UTC,
        the system will select key dates that appear to have their anniversary the next day.

        :return: the res.partner.date records
        """
        today = fields.Date.context_today(self)
        month_and_day = fields.Date.from_string(today).strftime('%m-%d')

        self.env.cr.execute("""
            SELECT d.id
            FROM res_partner_date d
            WHERE d.month_and_day = %s
            AND d.diffusion = true
            """, (month_and_day, ))

        key_date_ids = [r[0] for r in self.env.cr.fetchall()]
        return self.browse(key_date_ids)
