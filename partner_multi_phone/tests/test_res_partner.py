# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestResPartner(common.TransactionCase):

    def test_phone_extension_not_digit(self):
        with self.assertRaises(ValidationError):
            self.env['res.partner'].create({
                'name': 'Partner 1',
                'phone_extension': 'abcd',
            })

    def test_phone_other_extension_not_digit(self):
        with self.assertRaises(ValidationError):
            self.env['res.partner'].create({
                'name': 'Partner 2',
                'phone_other_extension': 'abcd',
            })

    def test_phone_extension_is_digit(self):
        partner = self.env['res.partner'].create({
            'name': 'Partner 1',
            'phone_extension': '123',
        })
        self.assertEqual(partner.phone_extension, '123')

    def test_phone_other_extension_is_digit(self):
        partner = self.env['res.partner'].create({
            'name': 'Partner 2',
            'phone_other_extension': '123',
        })
        self.assertEqual(partner.phone_other_extension, '123')
