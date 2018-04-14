# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerWithExtraPhones(models.Model):

    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']

    phone_main = fields.Selection(
        string='Main Phone', selection=[
            ('work', 'Work'),
            ('mobile', 'Mobile'),
            ('home', 'Home'),
            ('other', 'Other'),
        ])
    phone_home = fields.Char(string='Home')
    phone_other = fields.Char(string='Other')

    @api.onchange('phone_home', 'country_id', 'company_id')
    def _onchange_phone_home_validation(self):
        if self.phone_home:
            self.phone_home = self.phone_format(self.phone_home)

    @api.onchange('phone_other', 'country_id', 'company_id')
    def _onchange_phone_other_validation(self):
        if self.phone_other:
            self.phone_other = self.phone_format(self.phone_other)
