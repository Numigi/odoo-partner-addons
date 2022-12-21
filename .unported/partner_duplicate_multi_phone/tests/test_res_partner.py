# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.api import Environment
from odoo.tests import common


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        # Test using the demo user to prevent bugs related with access rights.
        cls.env = Environment(cls.env.cr, cls.env.ref('base.user_demo').id, {})

        cls.partner_1_phone = '+1 (450) 555-2671'
        cls.partner_1_mobile = '+1 (450) 678-4529'

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Hadi',
            'country_id': cls.env.ref('base.ca').id,
            'phone': cls.partner_1_phone,
            'mobile': cls.partner_1_mobile,
        })

        cls.partner_2_phone_other = '450-222-3456'
        cls.partner_2_phone_home = '581-999-5555'

        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Cohen',
            'country_id': cls.env.ref('base.ca').id,
            'phone_other': cls.partner_2_phone_other,
            'phone_home': cls.partner_2_phone_home,
        })

    def test_compute_phone_indexed(self):
        self.assertEqual('14505552671', self.partner_1.phone_indexed)

    def test_compute_mobile_indexed(self):
        self.assertEqual('14506784529', self.partner_1.mobile_indexed)

    def test_compute_phone_other_indexed(self):
        self.assertEqual('14502223456', self.partner_2.phone_other_indexed)

    def test_compute_phone_home_indexed(self):
        self.assertEqual('15819995555', self.partner_2.phone_home_indexed)

    def test_create_partner_with_duplicate_phone_home(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'country_id': self.env.ref('base.ca').id,
            'phone_home': '14506784529',
        })
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_mobile(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'country_id': self.env.ref('base.ca').id,
            'mobile': '14506784529'
        })
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_phone(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'phone': '14502223456',
        })
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_phone_other(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'phone_other': '14502223456',
        })
        self.assertEqual(len(self.partner_3.duplicate_ids), 1)

    def test_create_partner_with_duplicate_phone_numbers(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner XYZ',
            'country_id': self.env.ref('base.ca').id,
            'phone_other': '14502223456',
            'phone_home': '14506784529',
        })
        self.assertTrue(self.partner_3.duplicate_ids)
        self.assertEqual(len(self.partner_3.duplicate_ids), 2)

    def test_write_with_duplicate_phone(self):
        self.partner_2.write({'phone_home': '14506784529'})
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_write_with_duplicate_mobile(self):
        self.partner_2.write({'mobile': '14506784529'})
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_write_with_duplicate_phone_other(self):
        self.partner_1.write({
            'phone_other': self.partner_2_phone_other,
        })
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_write_with_duplicate_phone_home(self):
        self.partner_1.write({'phone_home': '(581) 999-5555'})
        self.assertTrue(self.partner_2.duplicate_ids)

    def test_duplicate_can_not_be_created_twice(self):
        partners = self.partner_1 | self.partner_2
        self.partner_2.write({'mobile': '14506784529'})
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners.ids),
            ('partner_2_id', 'in', partners.ids),
        ])
        self.assertEqual(len(duplicates), 1)

        self.partner_2.phone = '4505552671'
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners.ids),
            ('partner_2_id', 'in', partners.ids),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_partner_is_not_dupplicate_with_its_parent(self):
        self.partner_1.write({
            'parent_id': self.partner_2.id,
            'phone_other': self.partner_2_phone_other,
        })
        self.assertFalse(self.partner_2.duplicate_ids)

    def test_on_duplicate_create_cron__parent_partners_with_same_phone_excluded(self):
        self.partner_1.write({
            'parent_id': self.partner_2.id,
            'phone_other': self.partner_2_phone_other,
        })
        cron = self.env.ref('partner_duplicate_mgmt.ir_cron_create_duplicates')
        cron.sudo().method_direct_trigger()
        self.assertFalse(self.partner_2.duplicate_ids)
