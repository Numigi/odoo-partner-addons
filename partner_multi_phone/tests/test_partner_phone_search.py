# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestPartnerPhoneSearch(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.phone_number = '+1 (450) 922-3434'
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Partner A',
            'phone': cls.phone_number,
        })

        cls.phone_number_digit_only = '4509223434'
        cls.wrong_number = '4509224444'

    def _search_partners(self, phone):
        return self.env['res.partner'].with_context(
            search_partner_multi_phone=True).search([('phone', 'ilike', phone)])

    def test_search_partner_from_phone(self):
        result = self._search_partners(self.phone_number_digit_only)
        self.assertIn(self.partner_a, result)

    def test_search_partner_from_mobile(self):
        self.partner_a.phone = None
        self.partner_a.mobile = self.phone_number
        result = self._search_partners(self.phone_number_digit_only)
        self.assertIn(self.partner_a, result)

    def test_search_partner_from_phone_home(self):
        self.partner_a.phone = None
        self.partner_a.phone_home = self.phone_number
        result = self._search_partners(self.phone_number_digit_only)
        self.assertIn(self.partner_a, result)

    def test_search_partner_from_phone_other(self):
        self.partner_a.phone = None
        self.partner_a.phone_other = self.phone_number
        result = self._search_partners(self.phone_number_digit_only)
        self.assertIn(self.partner_a, result)

    def test_search_partner_from_phone_not_found(self):
        result = self._search_partners(self.wrong_number)
        self.assertNotIn(self.partner_a, result)

    def test_search_partner_from_mobile_not_found(self):
        self.partner_a.phone = None
        self.partner_a.mobile = self.phone_number
        result = self._search_partners(self.wrong_number)
        self.assertNotIn(self.partner_a, result)

    def test_search_partner_from_phone_home_not_found(self):
        self.partner_a.phone = None
        self.partner_a.phone_home = self.phone_number
        result = self._search_partners(self.wrong_number)
        self.assertNotIn(self.partner_a, result)

    def test_search_partner_from_phone_other_not_found(self):
        self.partner_a.phone = None
        self.partner_a.phone_other = self.phone_number
        result = self._search_partners(self.wrong_number)
        self.assertNotIn(self.partner_a, result)
