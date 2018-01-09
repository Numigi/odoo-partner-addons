# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from openerp.exceptions import UserError


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.group = cls.env.ref(
            'partner_duplicate_mgmt.group_duplicate_partners_control')
        cls.env.user.write({'groups_id': [(4, cls.group.id)]})

        cls.partner_1 = cls.env['res.partner'].create({
            'name': '11 Big Partner inc.',
            'is_company': True,
        })
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'My Partner inc.',
            'is_company': True,
        })
        cls.partner_3 = cls.env['res.partner'].create({
            'name': '33 Big Partner',
            'is_company': True,
        })

    def test_01_partner_indexed_name(self):
        self.assertEqual(self.partner_1.indexed_name, 'big partner')

        self.partner_1.write({'name': '123 CANADA Pince'})
        self.assertEqual(self.partner_1.indexed_name, 'pince')

    def test_02_partner_indexed_name_with_accent(self):
        partner_4 = self.env['res.partner'].create({
            'name': 'Julien Jézequel',
        })
        partner_5 = self.env['res.partner'].create({
            'name': 'Julien Jezequel',
        })

        self.assertEqual(partner_4.indexed_name, 'julien jezequel')
        self.assertEqual(partner_5.indexed_name, 'julien jezequel')
        self.assertIn(partner_4, partner_5.duplicate_ids)

    def test_03_create_new_partner_compute_duplicates(self):
        self.assertTrue(self.partner_3.duplicate_ids)
        self.assertEqual(self.partner_3.duplicate_count, 1)
        self.assertIn(self.partner_1, self.partner_3.duplicate_ids)

        self.assertIn(self.partner_1.name, self.partner_3.message_ids[0].body)

    def test_04_edit_partner_compute_duplicates(self):
        self.assertEqual(self.partner_2.duplicate_count, 0)

        self.partner_2.write({'name': '22 Bigg Partner'})
        self.assertTrue(self.partner_2.duplicate_ids)
        self.assertEqual(self.partner_2.duplicate_count, 2)
        self.assertIn(self.partner_1, self.partner_2.duplicate_ids)
        self.assertIn(self.partner_3, self.partner_2.duplicate_ids)

        self.assertIn(
            '11 Big Partner inc.', self.partner_2.message_ids[0].body)
        self.assertIn('33 Big Partner', self.partner_2.message_ids[0].body)

    def test_05_should_not_select_more_than_2_partners_to_merge(self):
        partners = self.partner_1 | self.partner_2 | self.partner_3
        with self.assertRaises(UserError):
            partners.action_merge()

    def test_06_should_not_create_new_duplicate_line(self):
        partners = self.partner_1 | self.partner_3
        partners.action_merge()
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners.ids),
            ('partner_2_id', 'in', partners.ids),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_07_merge_selected_contacts_action_is_unlinked(self):
        action = self.env['ir.actions.act_window'].search([
            ('name', '=', 'Merge Selected Contacts')])
        self.assertFalse(action)

    def test_08_disable_duplicate_check(self):
        partner = self.env['res.partner'].create({
            'name': 'Test disable check',
        })
        ctx = self.env.context.copy()
        ctx.update({'disable_duplicate_check': True})
        partner.with_context(ctx).copy()
        self.assertFalse(partner.duplicate_count)

    def test_09_merge_partners_similarity_1(self):
        # Similarity of these 2 partners : 0.53
        partner_4 = self.env['res.partner'].create({
            'name': 'Julienjez',
        })
        partner_5 = self.env['res.partner'].create({
            'name': 'Julyenjez',
        })

        similarity = self.env['res.partner']._get_min_similarity('Julienjez')
        self.assertEqual(similarity, '0.5')
        self.assertIn(partner_4, partner_5.duplicate_ids)

    def test_10_merge_partners_similarity_2(self):
        # Similarity of these 2 partners : 0.67
        partner_4 = self.env['res.partner'].create({
            'name': 'Julienjezequel',
        })
        partner_5 = self.env['res.partner'].create({
            'name': 'Julyenjezequel',
        })

        similarity = (
            self.env['res.partner']._get_min_similarity('Julienjezequel'))
        self.assertEqual(similarity, '0.6')
        self.assertIn(partner_4, partner_5.duplicate_ids)

    def test_11_merge_partners_similarity_3(self):
        # Similarity of these 2 partners : 0.63
        partner_4 = self.env['res.partner'].create({
            'name': 'Julien Jezequel Breard',
        })
        partner_5 = self.env['res.partner'].create({
            'name': 'Julyen Jezequel Brearr',
        })

        similarity = (
            self.env['res.partner']._get_min_similarity(
                'Julien Jezequel Breard'))
        self.assertEqual(similarity, '0.7')
        self.assertNotIn(partner_4, partner_5.duplicate_ids)

    def test_12_raise_error_when_try_to_merge_company_with_contact(self):
        self.partner_4 = self.env['res.partner'].create({
            'name': 'Julien',
        })

        partners = self.partner_1 | self.partner_4
        with self.assertRaises(UserError):
            partners.action_merge()

    def test_13_should_not_merge_company_with_contact(self):
        self.partner_4 = self.env['res.partner'].create({
            'name': 'Partner',
        })
        self.assertFalse(self.partner_4.duplicate_ids)

    def test_14_should_merge_2_companies_if_type_is_changed(self):
        self.partner_4 = self.env['res.partner'].create({
            'name': 'Partner',
        })
        self.partner_4.write({'is_company': True})
        self.assertTrue(self.partner_4.duplicate_ids)

    def test_15_should_not_merge_contacts_with_different_parents(self):
        self.partner_1.write({
            'child_ids': [(0, 0, {'name': 'Julien'})]
        })
        self.partner_2.write({
            'child_ids': [(0, 0, {'name': 'Julien'})]
        })
        self.assertFalse(self.partner_2.child_ids.duplicate_ids)

    def test_16_merge_contact_with_parent_and_contact_without_parent(self):
        partner_3 = self.env['res.partner'].create({
            'name': 'Partner Test 3',
            'company_type': 'person',
        })
        self.partner_2.write({
            'child_ids': [(0, 0, {'name': 'Partner Test 4'})]
        })
        self.assertIn(self.partner_2.child_ids, partner_3.duplicate_ids)

    def test_17_should_not_merge_entity_with_child(self):
        self.partner_1.write({
            'child_ids': [(0, 0, {'name': 'Big Partner'})]
        })
        self.assertFalse(self.partner_1.child_ids.duplicate_ids)
