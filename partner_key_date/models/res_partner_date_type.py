# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta
from odoo import fields, models


class ResPartnerDateType(models.Model):

    _name = "res.partner.date.type"
    _inherit = ["mail.thread"]
    _description = "Contact Key Date Type"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    mail_template_id = fields.Many2one(
        "mail.template",
        "Mail Template",
        ondelete="restrict",
        domain="[('model', '=', 'res.partner.date')]",
    )
    diffusion_delta = fields.Integer(
        help="Allows to send the anniversary email a number of days ahead of the key date."
    )

    def _find_anniversary_dates(self):
        """Find anniversary dates.

        This method is used to find dates for which the anniversary is today.

        The time zone of the user is used to select dates.
        Otherwise, if the function is called at 20h00 in Canada, and the system timezone is UTC,
        the system will select key dates that appear to have their anniversary the next day.

        :return: the res.partner.date records
        """
        today = fields.Date.context_today(self) + timedelta(self.diffusion_delta)
        month_and_day = fields.Date.from_string(today).strftime("%m-%d")
        return self.env["res.partner.date"].search([
            ("month_and_day", "=", month_and_day),
            ("date_type_id", "=", self.id),
            ("diffusion", "=", True),
        ])
