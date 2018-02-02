# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.exceptions import UserError

import random


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

        cls.group = cls.env.ref(
            'partner_duplicate_mgmt.group_contacts_merge_account_moves')

        cls.duplicate_email = cls.env['res.partner.duplicate.field'].create({
            'field_id': cls.field_email.id,
            'sequence': 5,
        })
        cls.duplicate_state = cls.env['res.partner.duplicate.field'].create({
            'field_id': cls.field_state.id,
            'sequence': 6,
        })

        cls.company_1 = cls.env['res.partner'].create({
            'name': '123 Company inc.',
            'is_company': True,
            'state_id': cls.state_on.id,
        })
        cls.company_2 = cls.env['res.partner'].create({
            'name': '456 Coompany inc.',
            'is_company': True,
        })

        cls.contact_1 = cls.env['res.partner'].create({
            'name': '123 Partner inc.',
            'email': 'contact_123@localhost',
            'parent_id': cls.company_1.id,
        })
        cls.contact_2 = cls.env['res.partner'].create({
            'name': '456 Paartner inc.',
            'email': 'partners@localhost',
            'state_id': cls.state_qc.id,
        })

        cls.bank_1 = cls.env['res.partner.bank'].create({
            'acc_number': 1111,
            'partner_id': cls.contact_1.id,
        })
        cls.bank_2 = cls.env['res.partner.bank'].create({
            'acc_number': 2222,
            'partner_id': cls.contact_2.id,
        })

        cls.attachment_1 = cls.env['ir.attachment'].create({
            'name': 'Attachment 1',
            'res_model': 'res.partner',
            'res_id': cls.contact_1.id,
        })
        cls.attachment_2 = cls.env['ir.attachment'].create({
            'name': 'Attachment 1',
            'res_model': 'res.partner',
            'res_id': cls.contact_2.id,
        })

        cls.contacts = [cls.contact_1.id, cls.contact_2.id]
        cls.companies = [cls.company_1.id, cls.company_2.id]

        cls.contact_dup = cls.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', cls.contacts),
            ('partner_2_id', 'in', cls.contacts),
        ])
        assert cls.contact_dup

        cls.contact_dup.open_partner_merge_wizard()
        cls.contact_merge_lines = cls.contact_dup.merge_line_ids

        cls.company_dup = cls.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', cls.companies),
            ('partner_2_id', 'in', cls.companies),
        ])
        assert cls.company_dup

        cls.company_dup.open_partner_merge_wizard()
        cls.company_merge_lines = cls.company_dup.merge_line_ids

    def test_01_cron_executed_twice_wont_create_2_duplicates(self):
        self.cron.method_direct_trigger()
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.contacts),
            ('partner_2_id', 'in', self.contacts),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_02_duplicates_where_partner1_equals_partner2_are_ignored(self):
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', '=', self.contact_1.id),
            ('partner_2_id', '=', self.contact_1.id),
        ])
        self.assertEqual(len(duplicates), 0)

    def test_03_reversed_and_normal_duplicate_of_duplicate_are_ignored(self):
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.contacts),
            ('partner_2_id', 'in', self.contacts),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_04_create_new_duplicate_adds_message_to_chatter(self):
        self.assertEqual(len(self.contact_2.message_ids), 2)
        self.assertIn(self.contact_1.name, self.contact_2.message_ids[0].body)

    def test_05_char_field_merge_line_created_correctly(self):
        merge_lines = self.contact_merge_lines
        merge_line = merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_email)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, 'partners@localhost')
        self.assertEqual(merge_line.partner_2_value, 'contact_123@localhost')

    def test_06_many2one_field_merge_line_created_correctly(self):
        merge_line = self.contact_merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_state)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, 'Quebec')
        self.assertEqual(merge_line.partner_2_value, 'Ontario')

    def test_07_merge_partners_update_char_field_partner_2_preserved(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})

        self.contact_merge_lines.write({'partner_1_selected': True})
        self.contact_merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_email
        ).write({'partner_2_selected': True})

        self.contact_dup.merge_partners()

        self.assertEqual(self.contact_dup.state, 'merged')
        self.assertEqual(self.contact_1.email, 'partners@localhost')

    def test_08_merge_partners_update_char_field(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_email
        ).write({'partner_1_selected': True})
        self.contact_dup.merge_partners()

        self.assertEqual(self.contact_2.email, 'contact_123@localhost')

    def test_09_merge_partners_update_many2one_field(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_state
        ).write({'partner_1_selected': True})
        self.contact_dup.merge_partners()

        self.assertEqual(self.contact_2.state_id, self.state_on)

    def test_10_partner_not_conserved_should_be_archived(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        self.assertTrue(self.contact_1)
        self.assertTrue(self.contact_2)

        self.assertFalse(self.contact_1.active)
        self.assertTrue(self.contact_2.active)

        self.assertEqual(len(self.contact_1.message_ids), 2)
        self.assertIn(self.contact_2.name, self.contact_1.message_ids[0].body)

    def test_11_contact_merge_doesnt_affect_message_ids(self):
        self.assertEqual(len(self.contact_1.message_ids), 1)
        self.assertEqual(len(self.contact_2.message_ids), 2)

        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        self.assertEqual(len(self.contact_1.message_ids), 2)
        self.assertEqual(len(self.contact_2.message_ids), 3)
        self.assertNotIn(
            self.contact_1.message_ids[0], self.contact_2.message_ids)
        self.assertNotIn(
            self.contact_1.message_ids[1], self.contact_2.message_ids)

    def test_12_contacts_merger_should_merge_one2many_field(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        self.assertIn(self.bank_1, self.contact_2.bank_ids)
        self.assertIn(self.bank_2, self.contact_2.bank_ids)

    def test_13_companies_merger_shouldnt_merge_one2many_field(self):
        self.bank_1.write({'partner_id': self.company_1.id})
        self.bank_2.write({'partner_id': self.company_2.id})

        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertEqual(self.bank_1.partner_id, self.company_1)
        self.assertEqual(self.bank_2.partner_id, self.company_2)

    def test_14_contacts_merger_should_merge_attachments(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        self.assertEqual(self.attachment_1.res_id, self.contact_2.id)
        self.assertEqual(self.attachment_2.res_id, self.contact_2.id)

    def test_15_companies_merger_shouldnt_merge_attachments(self):
        self.attachment_1.write({'res_id': self.company_1.id})
        self.attachment_2.write({'res_id': self.company_2.id})

        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertEqual(self.attachment_1.res_id, self.company_1.id)
        self.assertEqual(self.attachment_2.res_id, self.company_2.id)

    def test_16_merge_partners_doesnt_affect_null_values(self):
        self.contact_2.write({'phone': '4155552671'})
        self.assertFalse(self.contact_1.phone)

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_merge_lines.write({'partner_1_selected': True})
        self.contact_dup.merge_partners()

        self.assertFalse(self.contact_1.phone)

    def test_17_action_resolve(self):
        dup = self.contact_dup
        self.assertEqual(dup.state, 'to_validate')
        dup.action_resolve()
        self.assertEqual(dup.state, 'resolved')

    def test_18_companies_merger_makes_src_partner_child_of_dst_partner(self):
        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertEqual(self.company_1.parent_id, self.company_2)

    def test_19_companies_merger_moves_children_to_dst_partner(self):
        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertIn(self.contact_1, self.company_2.child_ids)
        self.assertFalse(self.company_1.child_ids)

    def create_invoice(self, partner):
        self.currency = self.env['res.currency'].search(
            [('name', '=', 'EUR')]
        )
        self.product = self.env['product.product'].create({
            'name': 'Product',
        })
        self.account_1 = self.env['account.account'].create({
            'code': random.randint(100, 999),
            'name': 'Payable Account',
            'reconcile': True,
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
        })
        self.account_2 = self.env['account.account'].create({
            'code': random.randint(100, 999),
            'name': 'Expenses Account',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
        })
        partner.write({
            'property_account_payable_id': self.account_2.id,
        })
        self.journal = self.env['account.journal'].create({
            'name': 'Journal',
            'type': 'bank',
            'code': str(random.randint(100, 999)),
        })
        self.account_invoice_line = self.env['account.invoice.line'].create({
            'name': 'My line 1',
            'product_id': self.product.id,
            'account_id': self.account_2.id,
            'price_unit': '20',
        })
        self.account_invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'account_id': self.account_1.id,
            'journal_id': self.journal.id,
            'currency_id': self.currency.id,
            'invoice_line_ids': [(4, self.account_invoice_line.id)],
            'type': 'in_invoice',
        })

        return self.account_invoice

    def test_20_cannot_merge_contact_with_account_moves(self):
        invoice = self.create_invoice(self.contact_2)
        invoice.action_invoice_open()

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_merge_lines.write({'partner_1_selected': True})

        with self.assertRaises(UserError):
            self.contact_dup.merge_partners()

    def test_21_special_group_can_merge_contacts_with_account_moves(self):
        self.env.user.write({'groups_id': [(4, self.group.id)]})

        invoice = self.create_invoice(self.contact_2)
        invoice.action_invoice_open()

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_merge_lines.write({'partner_1_selected': True})

        self.contact_dup.merge_partners()
        self.assertEqual(invoice.move_id.partner_id, self.contact_1)

    def test_22_compute_warning_message_partner_1_with_account_moves(self):
        self.assertFalse(self.contact_dup.warning_message)
        self.env.user.write({'groups_id': [(4, self.group.id)]})

        invoice = self.create_invoice(self.contact_2)
        invoice.action_invoice_open()

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_dup.onchange_partner_preserved_id()

        self.assertIn(self.contact_2.name, self.contact_dup.warning_message)

    def _get_current_duplicates(self, id_start):
        return self.env['res.partner.duplicate'].search([
            ('partner_1_id', '>=', id_start),
            ('partner_2_id', '>=', id_start),
        ])

    def test_23_cron_executed_correctly(self):
        # Similarity of these 2 partners : 0.53
        first_partner = self.env['res.partner'].create({'name': 'Julienjez'})
        self.env['res.partner'].create({'name': 'Julyenjez'})

        # Similarity of these 2 partners : 0.62
        self.env['res.partner'].create({'name': 'Julienbreard'})
        self.env['res.partner'].create({'name': 'Julyenbreard'})

        # Similarity of these 2 partners : 0.76
        self.env['res.partner'].create({'name': 'Julien Jezequel Breard'})
        self.env['res.partner'].create({'name': 'Julyen Jezequel Breard'})

        self._get_current_duplicates(first_partner.id).unlink()
        self.cron.method_direct_trigger()

        duplicates_generated_2 = self._get_current_duplicates(first_partner.id)
        self.assertEqual(len(duplicates_generated_2), 3)
