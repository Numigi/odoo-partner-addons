# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from ddt import ddt, data, unpack
from itertools import permutations
from odoo.api import Environment
from odoo.exceptions import UserError, ValidationError
from odoo.tests import common
from odoo import SUPERUSER_ID

import random


class PartnerDuplicateCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Test using the demo user to prevent bugs related with access rights.
        cls.env = Environment(cls.env.cr, cls.env.ref('base.user_demo').id, {})

        cls.state_on = cls.env.ref('base.state_ca_on')
        cls.state_qc = cls.env.ref('base.state_ca_qc')

        cls.cron = cls.env.ref('partner_duplicate_mgmt.ir_cron_create_duplicates')

        cls.account_move_group = cls.env.ref(
            'partner_duplicate_mgmt.group_contacts_merge_account_moves')

        cls.duplicate_email = cls.env.ref(
            'partner_duplicate_mgmt.duplicate_field_email')
        cls.duplicate_state = cls.env.ref(
            'partner_duplicate_mgmt.duplicate_field_state_id')

        cls.company_1 = cls.env['res.partner'].create({
            'name': 'Company 1',
            'is_company': True,
            'state_id': cls.state_on.id,
        })
        cls.company_2 = cls.env['res.partner'].create({
            'name': 'Coompany 1',
            'is_company': True,
        })

        cls.contact_1 = cls.env['res.partner'].create({
            'name': 'Partner inc.',
            'email': 'contact_123@localhost',
            'parent_id': cls.company_1.id,
        })
        cls.contact_2 = cls.env['res.partner'].create({
            'name': 'Paartner inc.',
            'email': 'partners@localhost',
            'state_id': cls.state_qc.id,
        })

        cls.bank_1 = cls.env['res.partner.bank'].create({
            'acc_number': '1111',
            'partner_id': cls.contact_1.id,
        })
        cls.bank_2 = cls.env['res.partner.bank'].create({
            'acc_number': '2222',
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


class TestResPartnerDuplicate(PartnerDuplicateCase):

    def test_cron_executed_twice_wont_create_2_duplicates(self):
        self.cron.sudo().method_direct_trigger()
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.contacts),
            ('partner_2_id', 'in', self.contacts),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_duplicates_where_partner1_equals_partner2_are_ignored(self):
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', '=', self.contact_1.id),
            ('partner_2_id', '=', self.contact_1.id),
        ])
        self.assertEqual(len(duplicates), 0)

    def test_reversed_and_normal_duplicate_of_duplicate_are_ignored(self):
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.contacts),
            ('partner_2_id', 'in', self.contacts),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_create_new_duplicate_adds_message_to_chatter(self):
        message = self._get_duplicate_partner_message(self.contact_2)
        self.assertEqual(len(message), 1)
        self.assertIn(self.contact_1.name, message.body)

    def test_char_field_merge_line_created_correctly(self):
        merge_lines = self.contact_merge_lines
        merge_line = merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_email)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, 'contact_123@localhost')
        self.assertEqual(merge_line.partner_2_value, 'partners@localhost')

    def test_many2one_field_merge_line_created_correctly(self):
        merge_line = self.contact_merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_state)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, self.state_on.display_name)
        self.assertEqual(merge_line.partner_2_value, self.state_qc.display_name)

    def test_merge_partners_update_char_field(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})

        email_line = self.contact_merge_lines.filtered(
            lambda so: so.duplicate_field_id == self.duplicate_email)
        email_line.write({'partner_1_selected': True})
        email_line.onchange_partner_1_selected()
        self.contact_dup.merge_partners()

        self.assertEqual(self.contact_dup.state, 'merged')
        self.assertEqual(self.contact_2.email, 'contact_123@localhost')

    def test_merge_partners_update_many2one_field(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})

        state_line = self.contact_merge_lines.filtered(
            lambda so: so.duplicate_field_id == self.duplicate_state)
        state_line.write({'partner_1_selected': True})
        state_line.onchange_partner_1_selected()
        self.contact_dup.merge_partners()

        self.assertEqual(self.contact_2.state_id, self.state_on)

    def test_partner_not_conserved_should_be_archived(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        self.assertTrue(self.contact_1)
        self.assertTrue(self.contact_2)

        self.assertFalse(self.contact_1.active)
        self.assertTrue(self.contact_2.active)

        message = self._get_archived_partner_message(self.contact_1)
        self.assertEqual(len(message), 1)
        self.assertIn(self.contact_2.name, message.body)

    def test_contact_merge_doesnt_affect_message_ids(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        archived_message = self._get_archived_partner_message(self.contact_1)
        preserved_message = self._get_preserved_partner_message(self.contact_2)

        self.assertEqual(len(archived_message), 1)
        self.assertEqual(len(preserved_message), 1)

        assert archived_message not in self.contact_2.message_ids
        assert preserved_message not in self.contact_1.message_ids

    def test_contacts_merger_should_merge_one2many_field(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        self.assertIn(self.bank_1, self.contact_2.bank_ids)
        self.assertIn(self.bank_2, self.contact_2.bank_ids)

    def test_companies_merger_shouldnt_merge_one2many_field(self):
        self.bank_1.write({'partner_id': self.company_1.id})
        self.bank_2.write({'partner_id': self.company_2.id})

        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertEqual(self.bank_1.partner_id, self.company_1)
        self.assertEqual(self.bank_2.partner_id, self.company_2)

    def test_contacts_merger_should_merge_attachments(self):
        self.contact_dup.write({'partner_preserved_id': self.contact_2.id})
        self.contact_merge_lines.write({'partner_2_selected': True})
        self.contact_dup.merge_partners()

        self.assertEqual(self.attachment_1.res_id, self.contact_2.id)
        self.assertEqual(self.attachment_2.res_id, self.contact_2.id)

    def test_companies_merger_shouldnt_merge_attachments(self):
        self.attachment_1.write({'res_id': self.company_1.id})
        self.attachment_2.write({'res_id': self.company_2.id})

        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertEqual(self.attachment_1.res_id, self.company_1.id)
        self.assertEqual(self.attachment_2.res_id, self.company_2.id)

    def test_merge_partners_doesnt_affect_null_values(self):
        self.contact_2.write({'phone': '4155552671'})
        self.assertFalse(self.contact_1.phone)

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_merge_lines.write({'partner_1_selected': True})
        self.contact_dup.merge_partners()

        self.assertFalse(self.contact_1.phone)

    def test_action_resolve(self):
        dup = self.contact_dup
        self.assertEqual(dup.state, 'to_validate')
        dup.action_resolve()
        self.assertEqual(dup.state, 'resolved')

    def test_companies_merger_makes_src_partner_child_of_dst_partner(self):
        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertEqual(self.company_1.parent_id, self.company_2)

    def test_companies_merger_moves_children_to_dst_partner(self):
        self.company_dup.write({'partner_preserved_id': self.company_2.id})
        self.company_merge_lines.write({'partner_2_selected': True})
        self.company_dup.merge_partners()

        self.assertIn(self.contact_1, self.company_2.child_ids)
        self.assertFalse(self.company_1.child_ids)

    def create_invoice(self, partner):
        env = Environment(self.env.cr, SUPERUSER_ID, {})
        currency = env['res.currency'].search(
            [('name', '=', 'EUR')]
        )
        product = env['product.product'].create({
            'name': 'Product',
        })
        account_1 = env['account.account'].create({
            'code': random.randint(100, 999),
            'name': 'Payable Account',
            'reconcile': True,
            'user_type_id': env.ref(
                'account.data_account_type_payable').id,
        })
        account_2 = env['account.account'].create({
            'code': random.randint(100, 999),
            'name': 'Expenses Account',
            'user_type_id': env.ref(
                'account.data_account_type_expenses').id,
        })
        partner.write({
            'property_account_payable_id': account_2.id,
        })
        journal = env['account.journal'].create({
            'name': 'Journal',
            'type': 'bank',
            'code': str(random.randint(100, 999)),
        })
        account_invoice_line = env['account.invoice.line'].create({
            'name': 'My line 1',
            'product_id': product.id,
            'account_id': account_2.id,
            'price_unit': '20',
        })
        account_invoice = env['account.invoice'].create({
            'partner_id': partner.id,
            'account_id': account_1.id,
            'journal_id': journal.id,
            'currency_id': currency.id,
            'invoice_line_ids': [(4, account_invoice_line.id)],
            'type': 'in_invoice',
        })

        return account_invoice

    def test_cannot_merge_contact_with_account_moves(self):
        invoice = self.create_invoice(self.contact_2)
        invoice.action_invoice_open()

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_merge_lines.write({'partner_1_selected': True})

        self.env.user.write({'groups_id': [(3, self.account_move_group.id)]})

        with self.assertRaises(UserError):
            self.contact_dup.merge_partners()

    def test_special_group_can_merge_contacts_with_account_moves(self):
        self.env.user.write({'groups_id': [(4, self.account_move_group.id)]})

        invoice = self.create_invoice(self.contact_2)
        invoice.action_invoice_open()

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_merge_lines.write({'partner_1_selected': True})

        self.contact_dup.merge_partners()

        # The move is updated using a direct sql query.
        # Need to reload it before checking the new partner.
        invoice.move_id.refresh()

        self.assertEqual(invoice.move_id.partner_id, self.contact_1)

    def test_compute_warning_message_partner_1_with_account_moves(self):
        self.assertFalse(self.contact_dup.warning_message)
        self.env.user.write({'groups_id': [(4, self.account_move_group.id)]})

        invoice = self.create_invoice(self.contact_2)
        invoice.action_invoice_open()

        self.contact_dup.write({'partner_preserved_id': self.contact_1.id})
        self.contact_dup._onchange_check_contacts_with_journal_entries()

        self.assertIn(self.contact_2.name, self.contact_dup.warning_message)

    def test_cron_executed_correctly(self):
        # Similarity of these 2 partners : 0.53
        first_partner = self.env['res.partner'].create({'name': 'Julienjez'})
        self.env['res.partner'].create({'name': 'Julyenjez'})

        # Similarity of these 2 partners : 0.62
        self.env['res.partner'].create({'name': 'Julienbreard'})
        self.env['res.partner'].create({'name': 'Julyenbreard'})

        # Similarity of these 2 partners : 0.76
        self.env['res.partner'].create({'name': 'Julien Jezequel Breard'})
        self.env['res.partner'].create({'name': 'Julyen Jezequel Breard'})

        # Remove any existing duplicates.
        self.env['res.partner.duplicate'].search([]).sudo().unlink()

        # Run the cron.
        self.cron.sudo().method_direct_trigger()

        duplicates_generated = self.env['res.partner.duplicate'].search([
            ('partner_1_id', '>=', first_partner.id),
            ('partner_2_id', '>=', first_partner.id),
        ])

        self.assertEqual(len(duplicates_generated), 3)

    def test_when_partner_is_archived_duplicates_left_are_resolved(self):
        partner_1 = self.env['res.partner'].create({'name': 'Partner 1'})
        partner_2 = self.env['res.partner'].create({'name': 'Partner 2'})
        partner_3 = self.env['res.partner'].create({'name': 'Partner 3'})

        dup1 = self.env['res.partner.duplicate'].search([
            ('partner_1_id', '=', partner_1.id),
            ('partner_2_id', '=', partner_2.id)
        ])
        dup2 = self.env['res.partner.duplicate'].search([
            ('partner_1_id', '=', partner_1.id),
            ('partner_2_id', '=', partner_3.id)
        ])
        dup3 = self.env['res.partner.duplicate'].search([
            ('partner_1_id', '=', partner_2.id),
            ('partner_2_id', '=', partner_3.id)
        ])

        dup1.open_partner_merge_wizard()
        dup1.write({'partner_preserved_id': partner_2.id})
        dup1.merge_line_ids.write({'partner_2_selected': True})
        dup1.merge_partners()

        self.assertEqual(dup1.state, 'merged')
        self.assertEqual(dup2.state, 'resolved')
        self.assertEqual(dup3.state, 'to_validate')

    def _get_archived_partner_message(self, partner):
        return partner.message_ids.filtered(
            lambda m: "Merged into" in (m.body or "")
        )

    def _get_preserved_partner_message(self, partner):
        return partner.message_ids.filtered(
            lambda m: "Merged with" in (m.body or "")
        )

    def _get_duplicate_partner_message(self, partner):
        return partner.message_ids.filtered(
            lambda m: "Duplicate" in (m.body or "")
        )


@ddt
class TestMergeChildWithParent(PartnerDuplicateCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env['res.partner'].create({'name': 'Partner 1'})
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Partner 2',
            'parent_id': cls.partner_1.id,
        })
        cls.partner_3 = cls.env['res.partner'].create({
            'name': 'Partner 3',
            'parent_id': cls.partner_2.id,
        })

    def merge_partners(self, preserved_partner, archived_partner):
        duplicate_row = self.env['res.partner.duplicate'].create({
            'partner_1_id': preserved_partner.id,
            'partner_2_id': archived_partner.id,
            'partner_preserved_id': preserved_partner.id,
        })
        duplicate_row.merge_partners()

    @data(*permutations(['partner_1', 'partner_2', 'partner_3'], 2))
    @unpack
    def test_can_not_merge_partner_with_parent(self, key_1, key_2):
        preserved_partner = getattr(self, key_1)
        archived_partner = getattr(self, key_2)
        with pytest.raises(ValidationError):
            self.merge_partners(preserved_partner, archived_partner)

    def test_can_merge_partners_with_no_relation(self):
        self.partner_2.parent_id = False
        preserved_partner = self.partner_1
        archived_partner = self.partner_2
        self.merge_partners(preserved_partner, archived_partner)
        assert self.partner_2.active is False

    def test_can_merge_sibling_partners(self):
        self.partner_3.parent_id = self.partner_1
        preserved_partner = self.partner_2
        archived_partner = self.partner_3
        self.merge_partners(preserved_partner, archived_partner)
        assert self.partner_3.active is False
