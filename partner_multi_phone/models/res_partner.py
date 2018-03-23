# -*- coding: utf-8 -*-
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']

    phone_main = fields.Selection(
        string='Main Phone', selection=[
            ('work', 'Work'),
            ('mobile', 'Mobile'),
            ('home', 'Home'),
            ('other', 'Other'),
        ])
    phone_extension = fields.Char()
    phone_home = fields.Char(string='Home')
    phone_other = fields.Char(string='Other')
    phone_other_extension = fields.Char()

    @api.onchange('phone_home', 'country_id', 'company_id')
    def _onchange_phone_home_validation(self):
        if self.phone_home:
            self.phone_home = self.phone_format(self.phone_home)

    @api.onchange('phone_other', 'country_id', 'company_id')
    def _onchange_phone_other_validation(self):
        if self.phone_other:
            self.phone_other = self.phone_format(self.phone_other)

    @api.constrains('phone_extension')
    def _check_phone_extension(self):
        if self.phone_extension:
            self._check_extension_number(self.phone_extension)

    @api.constrains('phone_other_extension')
    def _check_phone_other_extension(self):
        if self.phone_other_extension:
            self._check_extension_number(self.phone_other_extension)

    def _check_extension_number(self, number):
        if not number.isdigit():
            raise ValidationError(
                _('The phone extension must contain only digits.'))
