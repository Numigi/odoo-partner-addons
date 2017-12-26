# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.exceptions import UserError


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

        cls.partners = [cls.contact_1.id, cls.contact_2.id]

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
            ('partner_1_id', '=', self.contact_1.id),
            ('partner_2_id', '=', self.contact_1.id),
        ])
        self.assertEqual(len(duplicates), 0)

    def test_04_reversed_and_normal_duplicate_of_duplicate_are_ignored(self):
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.partners),
            ('partner_2_id', 'in', self.partners),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_05_create_new_duplicate_adds_message_to_chatter(self):
        self.assertEqual(len(self.contact_2.message_ids), 2)
        self.assertIn(self.contact_1.name, self.contact_2.message_ids[0].body)

    def test_06_char_field_merge_line_created_correctly(self):
        merge_lines = self.merge_lines
        merge_line = merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_email)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, 'partners@localhost')
        self.assertEqual(merge_line.partner_2_value, 'contact_123@localhost')

    def test_07_many2one_field_merge_line_created_correctly(self):
        merge_line = self.merge_lines.filtered(
            lambda l: l.duplicate_field_id == self.duplicate_state)

        self.assertTrue(merge_line)
        self.assertEqual(merge_line.partner_1_value, 'Quebec')
        self.assertEqual(merge_line.partner_2_value, 'Ontario')

    def test_08_merge_partners_update_char_field_partner_2_preserved(self):
        self.duplicate.write({'partner_preserved_id': self.contact_1.id})

        self.merge_lines.write({'partner_1_selected': True})
        self.merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_email
        ).write({'partner_2_selected': True})

        self.duplicate.merge_partners()

        self.assertEqual(self.duplicate.state, 'merged')
        self.assertEqual(self.contact_1.email, 'partners@localhost')

    def test_09_merge_partners_update_char_field(self):
        self.duplicate.write({'partner_preserved_id': self.contact_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_email
        ).write({'partner_1_selected': True})
        self.duplicate.merge_partners()

        self.assertEqual(self.contact_2.email, 'contact_123@localhost')

    def test_10_merge_partners_update_many2one_field(self):
        self.duplicate.write({'partner_preserved_id': self.contact_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.merge_lines.filtered(
            lambda so: so.duplicate_field_id != self.duplicate_state
        ).write({'partner_1_selected': True})
        self.duplicate.merge_partners()

        self.assertEqual(self.contact_2.state_id, self.state_on)

    def test_11_partner_not_conserved_should_be_archived(self):
        self.duplicate.write({'partner_preserved_id': self.contact_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        self.assertTrue(self.contact_1)
        self.assertTrue(self.contact_2)

        self.assertFalse(self.contact_1.active)
        self.assertTrue(self.contact_2.active)

        self.assertEqual(len(self.contact_1.message_ids), 2)
        self.assertIn(self.contact_2.name, self.contact_1.message_ids[0].body)

    def test_12_contact_merge_doesnt_affect_message_ids(self):
        self.assertEqual(len(self.contact_1.message_ids), 1)
        self.assertEqual(len(self.contact_2.message_ids), 2)

        self.duplicate.write({'partner_preserved_id': self.contact_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        self.assertEqual(len(self.contact_1.message_ids), 2)
        self.assertEqual(len(self.contact_2.message_ids), 3)
        self.assertNotIn(
            self.contact_1.message_ids[0], self.contact_2.message_ids)
        self.assertNotIn(
            self.contact_1.message_ids[1], self.contact_2.message_ids)

    def test_13_contacts_merger_should_merge_one2many_field(self):
        self.duplicate.write({'partner_preserved_id': self.contact_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        self.assertIn(self.bank_1, self.contact_2.bank_ids)
        self.assertIn(self.bank_2, self.contact_2.bank_ids)

    def test_14_companies_merger_shouldnt_merge_one2many_field(self):
        self.bank_1.write({'partner_id': self.company_1.id})
        self.bank_2.write({'partner_id': self.company_2.id})

        partners = [self.company_1.id, self.company_2.id]
        duplicate = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners),
            ('partner_2_id', 'in', partners),
        ])
        self.assertTrue(duplicate)
        duplicate.open_partner_merge_wizard()
        merge_lines = duplicate.merge_line_ids

        duplicate.write({'partner_preserved_id': self.company_2.id})
        merge_lines.write({'partner_2_selected': True})
        duplicate.merge_partners()

        self.assertEqual(self.bank_1.partner_id, self.company_1)
        self.assertEqual(self.bank_2.partner_id, self.company_2)

    def test_15_contacts_merger_should_merge_attachments(self):
        self.duplicate.write({'partner_preserved_id': self.contact_2.id})
        self.merge_lines.write({'partner_2_selected': True})
        self.duplicate.merge_partners()

        self.assertEqual(self.attachment_1.res_id, self.contact_2.id)
        self.assertEqual(self.attachment_2.res_id, self.contact_2.id)

    def test_16_companies_merger_shouldnt_merge_attachments(self):
        self.attachment_1.write({'res_id': self.company_1.id})
        self.attachment_2.write({'res_id': self.company_2.id})

        partners = [self.company_1.id, self.company_2.id]
        duplicate = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners),
            ('partner_2_id', 'in', partners),
        ])
        self.assertTrue(duplicate)
        duplicate.open_partner_merge_wizard()
        merge_lines = duplicate.merge_line_ids

        duplicate.write({'partner_preserved_id': self.company_2.id})
        merge_lines.write({'partner_2_selected': True})
        duplicate.merge_partners()

        self.assertEqual(self.attachment_1.res_id, self.company_1.id)
        self.assertEqual(self.attachment_2.res_id, self.company_2.id)

    def test_17_merge_partners_doesnt_affect_null_values(self):
        self.contact_2.write({'phone': '4155552671'})
        self.assertFalse(self.contact_1.phone)

        self.duplicate.write({'partner_preserved_id': self.contact_1.id})
        self.merge_lines.write({'partner_1_selected': True})
        self.duplicate.merge_partners()

        self.assertFalse(self.contact_1.phone)

    def test_18_action_resolve(self):
        dup = self.duplicate
        self.assertEqual(dup.state, 'to_validate')
        dup.action_resolve()
        self.assertEqual(dup.state, 'resolved')

    def test_19_companies_merger_makes_src_partner_child_of_dst_partner(self):
        partners = [self.company_1.id, self.company_2.id]
        duplicate = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners),
            ('partner_2_id', 'in', partners),
        ])
        self.assertTrue(duplicate)
        duplicate.open_partner_merge_wizard()
        merge_lines = duplicate.merge_line_ids

        duplicate.write({'partner_preserved_id': self.company_2.id})
        merge_lines.write({'partner_2_selected': True})
        duplicate.merge_partners()

        self.assertEqual(self.company_1.parent_id, self.company_2)

    def test_20_companies_merger_moves_children_to_dst_partner(self):
        partners = [self.company_1.id, self.company_2.id]
        duplicate = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners),
            ('partner_2_id', 'in', partners),
        ])
        self.assertTrue(duplicate)
        duplicate.open_partner_merge_wizard()
        merge_lines = duplicate.merge_line_ids

        duplicate.write({'partner_preserved_id': self.company_2.id})
        merge_lines.write({'partner_2_selected': True})
        duplicate.merge_partners()

        self.assertIn(self.contact_1, self.company_2.child_ids)
        self.assertFalse(self.company_1.child_ids)

    def create_invoice(self):
        self.currency = self.env['res.currency'].search(
            [('name', '=', 'EUR')]
        )
        self.account_1 = self.env['account.account'].create({
            'code': '1234',
            'name': 'Payable Account',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
        })
        self.account_2 = self.env['account.account'].create({
            'code': '1708',
            'name': 'Expenses Account',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
        })
        self.account_invoice_line = self.env['account.invoice.line'].create({
            'name': 'My line 1',
            'account_id': self.account_2.id,
            'price_unit': '20',
        })
        self.account_invoice = self.env['account.invoice'].create({
            'partner_id': self.contact_2.id,
            'account_id': self.account_1.id,
            'currency_id': self.currency.id,
            'invoice_line_ids': [(4, self.account_invoice_line.id)],
            'type': 'in_invoice',
        })

        return self.account_invoice

    def test_21_cannot_merge_contact_with_account_moves(self):
        invoice = self.create_invoice()
        invoice.action_invoice_open()

        self.duplicate.write({'partner_preserved_id': self.contact_1.id})
        self.merge_lines.write({'partner_1_selected': True})

        with self.assertRaises(UserError):
            self.duplicate.merge_partners()

    def test_22_special_group_can_merge_contact_with_account_moves(self):
        group = self.env.ref(
            'partner_duplicate_mgmt.group_contacts_merge_account_moves')
        self.env.user.write({'groups_id': [(4, group.id)]})

        invoice = self.create_invoice()
        invoice.action_invoice_open()

        self.duplicate.write({'partner_preserved_id': self.contact_1.id})
        self.merge_lines.write({'partner_1_selected': True})

        self.duplicate.merge_partners()
        self.assertEqual(invoice.move_id.partner_id, self.contact_1)
