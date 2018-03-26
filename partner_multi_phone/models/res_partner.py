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
            _check_extension_number(self.phone_extension)

    @api.constrains('phone_other_extension')
    def _check_phone_other_extension(self):
        if self.phone_other_extension:
            _check_extension_number(self.phone_other_extension)


def _check_extension_number(extension):
    """Check that the given extension is valid.

    :param str extension: the extension to check
    """
    if not extension.isdigit():
        raise ValidationError(
            _('The phone extension must contain only digits.'))
