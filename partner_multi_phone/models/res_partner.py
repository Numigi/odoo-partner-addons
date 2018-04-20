# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

PHONE_FIELDS = ('phone', 'mobile', 'phone_home', 'phone_other')


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


class ResPartnerWithPhoneSearch(models.Model):

    _inherit = 'res.partner'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Allow searching partners from a phone number."""
        is_phone_search = (
            self._context.get('search_partner_multi_phone') and
            args and isinstance(args[0], (list, tuple)) and args[0][0] == 'phone'
        )
        if is_phone_search:
            phone_number = args[0][2]
            args = self._get_multi_phone_search_domain(phone_number)

        return super().search(args, offset=offset, limit=limit, order=order, count=count)

    def _get_multi_phone_search_domain(self, phone_number):
        """Get a domain expression for searching a phone number from any phone field.

        The returned domain allows to search a phone given only a series of digits.

        For example, searching 4504623434 would allow to find partners with the number
        +1 450-462-3434.

        :param phone_number: the phone number to search
        :return: a search domain
        """
        phone_expression = '%'.join(c for c in phone_number)
        return [
            '|', '|', '|',
            ('phone', 'ilike', phone_expression),
            ('mobile', 'ilike', phone_expression),
            ('phone_home', 'ilike', phone_expression),
            ('phone_other', 'ilike', phone_expression),
        ]
