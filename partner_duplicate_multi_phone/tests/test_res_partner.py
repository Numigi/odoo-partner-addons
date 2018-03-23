# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Hadi',
            'phone': '(415) 555-2671',
            'phone_extension': '333',
            'mobile': '+1 (415) 678-4529',
        })

        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Cohen',
            'phone_other': '415-222-3456',
            'phone_other_extension': '331',
            'phone_home': '581-999-5555',
        })

    def test_compute_phone_indexed(self):
        self.assertEqual('4155552671333', self.partner_1.phone_indexed)

    def test_compute_mobile_indexed(self):
        self.assertEqual('14156784529', self.partner_1.mobile_indexed)

    def test_compute_phone_other_indexed(self):
        self.assertEqual('4152223456331', self.partner_2.phone_other_indexed)

    def test_compute_phone_home_indexed(self):
        self.assertEqual('5819995555', self.partner_2.phone_home_indexed)

    def test_create_partner_with_duplicate_phone_home(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'phone_home': '14156784529',
        })
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_mobile(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'mobile': '14156784529'
        })
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_phone(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'phone': '4152223456',
            'phone_extension': '331'
        })
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_phone_other(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'phone_other': '4152223456',
            'phone_other_extension': '331'})
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_phone_numbers(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'phone_other': '4152223456',
            'phone_other_extension': '331',
            'phone_home': '14156784529',
        })
        self.assertTrue(self.partner_3.duplicate_ids)
        self.assertEqual(len(self.partner_3.duplicate_ids), 2)

    def test_write_with_duplicate_phone(self):
        self.partner_2.write({'phone_home': '14156784529'})
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_write_with_duplicate_mobile(self):
        self.partner_2.write({'mobile': '14156784529'})
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_write_with_duplicate_phone_other(self):
        self.partner_1.write({
            'phone_other': '(415) 222-3456',
            'phone_other_extension': '331',
        })
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_write_with_duplicate_phone_home(self):
        self.partner_1.write({'phone_home': '(581) 999-5555'})
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_duplicate_can_not_be_created_twice(self):
        partners = self.partner_1 | self.partner_2
        self.partner_2.write({'mobile': '14156784529'})
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners.ids),
            ('partner_2_id', 'in', partners.ids),
        ])
        self.assertEqual(len(duplicates), 1)

        self.partner_2.write({
            'phone': '4155552671',
            'phone_extension': '333',
        })
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners.ids),
            ('partner_2_id', 'in', partners.ids),
        ])
        self.assertEqual(len(duplicates), 1)
