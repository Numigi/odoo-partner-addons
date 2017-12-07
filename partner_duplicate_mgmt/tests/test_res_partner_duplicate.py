# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestResPartnerDuplicate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerDuplicate, cls).setUpClass()

        cls.field_email = cls.env.ref('base.field_res_partner_email')
        cls.field_state = cls.env.ref('base.field_res_partner_state_id')

        cls.state_on = cls.env.ref('base.state_ca_on')
        cls.state_qc = cls.env.ref('base.state_ca_qc')

        cls.cron = cls.env.ref(
            'partner_duplicate_mgmt.ir_cron_create_duplicates')

        cls.duplicate_email = cls.env['res.partner.duplicate.field'].create({
            'field_id': cls.field_email.id,
            'sequence': 5,
        })
        cls.duplicate_state = cls.env['res.partner.duplicate.field'].create({
            'field_id': cls.field_state.id,
            'sequence': 6,
        })

        cls.bank_1 = cls.env['res.partner.bank'].create({
            'acc_number': 1111,
        })
        cls.bank_2 = cls.env['res.partner.bank'].create({
            'acc_number': 2222,
        })

        cls.partner_1 = cls.env['res.partner'].create({
            'name': '123 Partner inc.',
            'is_company': True,
            'company_type': 'company',
            'email': 'partner_123@localhost',
            'state_id': cls.state_on.id,
            'bank_ids': [(4, cls.bank_1.id)],
        })

        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Partners inc.',
            'is_company': True,
            'company_type': 'company',
            'email': 'partners@localhost',
            'state_id': cls.state_qc.id,
            'bank_ids': [(4, cls.bank_2.id)],
        })

        cls.partners = [cls.partner_1.id, cls.partner_2.id]

        cls.duplicate = cls.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', cls.partners),
            ('partner_2_id', 'in', cls.partners),
        ])
        assert cls.duplicate

        cls.duplicate.open_partner_merge_wizard()
        cls.merge_lines = cls.duplicate.merge_line_ids

    def test_01_make_sure_that_first_duplicate_exists(self):
        self.assertTrue(self.duplicate)

    def test_02_cron_executed_twice_wont_create_2_duplicates(self):
        self.cron.method_direct_trigger()
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.partners),
            ('partner_2_id', 'in', self.partners),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_03_duplicates_where_partner1_equals_partner2_are_ignored(self):
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', '=', self.partner_1.id),
            ('partner_2_id', '=', self.partner_1.id),
        ])
        self.assertEqual(len(duplicates), 0)

    def test_04_reversed_and_normal_duplicate_of_duplicate_are_ignored(self):
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.partners),
            ('partner_2_id', 'in', self.partners),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_05_cron_creates_new_partner_duplicate(self):
        self.partner_3 = self.env['res.partner'].create({
            'name': 'Partner',
        })
        self.cron.method_direct_trigger()

        duplicates = self.env['res.partner.duplicate'].search([
            '|',
            ('partner_1_id', '=', self.partner_3.id),
            ('partner_2_id', '=', self.partner_3.id),
        ])
        self.assertEqual(len(duplicates), 2)

    def test_06_create_new_duplicate_adds_message_to_chatter(self):
        self.assertEqual(len(self.partner_2.message_ids), 2)
        self.assertIn(self.partner_1.name, self.partner_2.message_ids[0].body)

    def test_07_char_field_merge_line_created_correctly(self):
        merge_lines = self.merge_lines
        merge_line = merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_email)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, 'partners@localhost')
        self.assertEqual(merge_line.partner_2_value, 'partner_123@localhost')

    def test_08_many2one_field_merge_line_created_correctly(self):
        merge_line = self.merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_state)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, 'Quebec')
        self.assertEqual(merge_line.partner_2_value, 'Ontario')

    def test_09_merge_partners_update_char_field_partner_2_preserved(self):
        self.duplicate.write({'partner_preserved_id': self.partner_1.id})

        self.merge_lines.write({'partner_1_selected': True})
        self.merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_email
        ).write({'partner_2_selected': True})

        self.duplicate.merge_partners()

        self.assertEqual(self.duplicate.state, 'merged')
        self.assertEqual(self.partner_1.email, 'partners@localhost')

    def test_10_merge_partners_update_char_field(self):
        self.duplicate.write({'partner_preserved_id': self.partner_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_email
        ).write({'partner_1_selected': True})
        self.duplicate.merge_partners()

        self.assertEqual(self.partner_2.email, 'partner_123@localhost')

    def test_11_merge_partners_update_many2one_field(self):
        self.duplicate.write({'partner_preserved_id': self.partner_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_state
        ).write({'partner_1_selected': True})
        self.duplicate.merge_partners()

        self.assertEqual(self.partner_2.state_id, self.state_on)

    def test_12_partner_not_conserved_should_be_archived(self):
        self.duplicate.write({'partner_preserved_id': self.partner_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        # Verify that the two partners still exist
        self.assertTrue(self.partner_1.name)
        self.assertTrue(self.partner_2.name)

        self.assertFalse(self.partner_1.active)
        self.assertTrue(self.partner_2.active)

        self.assertEqual(len(self.partner_1.message_ids), 2)
        self.assertIn(self.partner_2.name, self.partner_1.message_ids[0].body)

    def test_13_should_not_merge_contacts_with_different_parents(self):
        self.partner_1.write({
            'child_ids': [(0, 0, {'name': 'Partner Test 3'})]
        })
        self.partner_2.write({
            'child_ids': [(0, 0, {'name': 'Partner Test 4'})]
        })
        self.cron.method_direct_trigger()

        contacts = [
            self.partner_1.child_ids[0].id,
            self.partner_2.child_ids[0].id]
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', contacts),
            ('partner_2_id', 'in', contacts),
        ])
        self.assertEqual(len(duplicates), 0)

    def test_14_merge_contact_with_parent_and_contact_without_parent(self):
        partner_3 = self.env['res.partner'].create({
            'name': 'Partner Test 3',
            'company_type': 'person',
        })
        self.partner_2.write({
            'child_ids': [(0, 0, {'name': 'Partner Test 4'})]
        })
        contacts = [partner_3.id, self.partner_2.child_ids[0].id]

        self.cron.method_direct_trigger()

        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', contacts),
            ('partner_2_id', 'in', contacts),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_15_merge_entity_with_contact(self):
        partner_3 = self.env['res.partner'].create({
            'name': 'Partner Test 3',
            'company_type': 'company',
        })
        self.partner_2.write({
            'child_ids': [(0, 0, {'name': 'Partner Test 4'})]
        })
        contacts = [partner_3.id, self.partner_2.child_ids[0].id]

        self.cron.method_direct_trigger()

        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', contacts),
            ('partner_2_id', 'in', contacts),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_16_should_not_merge_entity_with_child(self):
        self.partner_1.write({
            'child_ids': [(0, 0, {'name': '123 Partners'})]
        })
        contacts = [self.partner_1.id, self.partner_1.child_ids[0].id]

        self.cron.method_direct_trigger()

        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', contacts),
            ('partner_2_id', 'in', contacts),
        ])
        self.assertEqual(len(duplicates), 0)

    def test_17_partner_merge_doesnt_affect_message_ids(self):
        self.assertEqual(len(self.partner_1.message_ids), 1)
        self.assertEqual(len(self.partner_2.message_ids), 2)

        self.duplicate.write({'partner_preserved_id': self.partner_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        self.assertEqual(len(self.partner_1.message_ids), 2)
        self.assertEqual(len(self.partner_2.message_ids), 3)
        self.assertNotIn(
            self.partner_1.message_ids[0], self.partner_2.message_ids)
        self.assertNotIn(
            self.partner_1.message_ids[1], self.partner_2.message_ids)

    def test_18_merge_partners_update_many2many_field(self):
        self.duplicate.write({'partner_preserved_id': self.partner_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        # All the references which pointed to partner 1
        # point now to partner 2

        self.assertIn(self.bank_1, self.partner_2.bank_ids)
        self.assertIn(self.bank_2, self.partner_2.bank_ids)

    def test_19_merge_partners_merge_attachments(self):
        attachment_1 = self.env['ir.attachment'].create({
            'name': 'Attachment 1',
            'res_model': 'res.partner',
            'res_id': self.partner_1.id,
        })
        attachment_2 = self.env['ir.attachment'].create({
            'name': 'Attachment 1',
            'res_model': 'res.partner',
            'res_id': self.partner_2.id,
        })

        self.duplicate.write({'partner_preserved_id': self.partner_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.partner_2.id)
        ])

        self.assertIn(attachment_1, attachments)
        self.assertIn(attachment_2, attachments)

    def test_20_merge_partners_doesnt_affect_null_values(self):
        self.partner_2.write({'phone': '4155552671'})
        self.assertFalse(self.partner_1.phone)

        self.duplicate.write({'partner_preserved_id': self.partner_1.id})
        self.merge_lines.write({'partner_1_selected': True})
        self.duplicate.merge_partners()

        self.assertFalse(self.partner_1.phone)

    def test_21_action_resolve(self):
        dup = self.duplicate
        self.assertEqual(dup.state, 'to_validate')
        dup.action_resolve()
        self.assertEqual(dup.state, 'resolved')

        self.assertIn('resolved', dup.partner_1_id.message_ids[0].body)
        self.assertIn('resolved', dup.partner_2_id.message_ids[0].body)
