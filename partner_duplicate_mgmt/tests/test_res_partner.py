# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.api import Environment
from odoo.tests import common
from openerp.exceptions import UserError


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        # Test using the demo user to prevent bugs related with access rights.
        cls.env = Environment(cls.env.cr, cls.env.ref('base.user_demo').id, {})

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Big Partner',
            'is_company': True,
        })
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'My Partner',
            'is_company': True,
        })
        cls.partner_3 = cls.env['res.partner'].create({
            'name': 'Big Partner',
            'is_company': True,
        })

    def test_partner_indexed_name_is_lower_case(self):
        self.assertEqual(self.partner_1.indexed_name, 'big partner')

    def test_partner_indexed_name_with_accent(self):
        partner_4 = self.env['res.partner'].create({
            'name': 'Julien Jézequel',
        })
        partner_5 = self.env['res.partner'].create({
            'name': 'Julien Jezequel',
        })

        self.assertEqual(partner_4.indexed_name, 'julien jezequel')
        self.assertEqual(partner_5.indexed_name, 'julien jezequel')
        self.assertIn(partner_4, partner_5.duplicate_ids)

    def test_create_new_partner_compute_duplicates(self):
        self.assertTrue(self.partner_3.duplicate_ids)
        self.assertEqual(self.partner_3.duplicate_count, 1)
        self.assertIn(self.partner_1, self.partner_3.duplicate_ids)

        self.assertIn(self.partner_1.name, self.partner_3.message_ids[0].body)

    def test_edit_partner_compute_duplicates(self):
        self.assertEqual(self.partner_2.duplicate_count, 0)

        self.partner_2.write({'name': 'Bigg Partner'})
        self.assertTrue(self.partner_2.duplicate_ids)
        self.assertEqual(self.partner_2.duplicate_count, 2)
        self.assertIn(self.partner_1, self.partner_2.duplicate_ids)
        self.assertIn(self.partner_3, self.partner_2.duplicate_ids)

    def test_should_not_select_more_than_2_partners_to_merge(self):
        partners = self.partner_1 | self.partner_2 | self.partner_3
        with self.assertRaises(UserError):
            partners.action_merge()

    def test_should_not_create_new_duplicate_line(self):
        partners = self.partner_1 | self.partner_3
        partners.action_merge()
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners.ids),
            ('partner_2_id', 'in', partners.ids),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_merge_selected_contacts_action_is_unlinked(self):
        action = self.env['ir.actions.act_window'].search([
            ('name', '=', 'Merge Selected Contacts')])
        self.assertFalse(action)

    def test_disable_duplicate_check(self):
        partner = self.env['res.partner'].create({
            'name': 'Test disable check',
        })
        ctx = self.env.context.copy()
        ctx.update({'disable_duplicate_check': True})
        partner.with_context(ctx).copy()
        self.assertFalse(partner.duplicate_count)

    def test_merge_partners_similarity_1(self):
        # Similarity of these 2 partners : 0.53
        partner_4 = self.env['res.partner'].create({'name': 'Julienjez'})
        partner_5 = self.env['res.partner'].create({'name': 'Julyenjez'})

        similarity = self.env['res.partner']._get_min_similarity('Julienjez')
        self.assertEqual(similarity, '0.5')
        self.assertIn(partner_4, partner_5.duplicate_ids)

    def test_merge_partners_similarity_2(self):
        # Similarity of these 2 partners : 0.67
        partner_4 = self.env['res.partner'].create({'name': 'Julienjezequel'})
        partner_5 = self.env['res.partner'].create({'name': 'Julyenjezequel'})

        similarity = self.env['res.partner']._get_min_similarity('Julienjezequel')
        self.assertEqual(similarity, '0.6')
        self.assertIn(partner_4, partner_5.duplicate_ids)

    def test_merge_partners_similarity_3(self):
        # Similarity of these 2 partners : 0.63
        partner_4 = self.env['res.partner'].create({'name': 'Julien Jezequel Breard'})
        partner_5 = self.env['res.partner'].create({'name': 'Julyen Jezequel Brearr'})

        similarity = self.env['res.partner']._get_min_similarity('Julien Jezequel Breard')
        self.assertEqual(similarity, '0.7')
        self.assertNotIn(partner_4, partner_5.duplicate_ids)

    def test_raise_error_when_try_to_merge_company_with_contact(self):
        partner_4 = self.env['res.partner'].create({'name': 'Julien'})

        partners = self.partner_1 | partner_4
        with self.assertRaises(UserError):
            partners.action_merge()

    def test_company_is_not_proposed_as_duplicate_of_contact(self):
        partner_4 = self.env['res.partner'].create({'name': 'Big Partner', 'is_company': False})
        self.assertFalse(partner_4.duplicate_ids)

        partner_4.write({'is_company': True})
        partner_4.refresh()
        self.assertTrue(partner_4.duplicate_ids)

    def test_should_not_merge_contacts_with_different_parents(self):
        self.partner_1.write({
            'child_ids': [(0, 0, {'name': 'Julien'})]
        })
        self.partner_2.write({
            'child_ids': [(0, 0, {'name': 'Julien'})]
        })
        self.assertFalse(self.partner_2.child_ids.duplicate_ids)

    def test_merge_contact_with_parent_and_contact_without_parent(self):
        partner_3 = self.env['res.partner'].create({
            'name': 'Partner Test 3',
            'company_type': 'person',
        })
        self.partner_2.write({
            'child_ids': [(0, 0, {'name': 'Partner Test 4'})]
        })
        self.assertIn(self.partner_2.child_ids, partner_3.duplicate_ids)

    def test_should_not_merge_entity_with_child(self):
        self.partner_1.write({
            'child_ids': [(0, 0, {'name': 'Big Partner'})]
        })
        self.assertFalse(self.partner_1.child_ids.duplicate_ids)
