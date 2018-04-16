# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.api import Environment
from odoo.tests import common


class TestResPartnerChangeParent(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerChangeParent, cls).setUpClass()

        # Test using the demo user to prevent bugs related with access rights.
        cls.env = Environment(cls.env.cr, cls.env.ref('base.user_demo').id, {})

        cls.company_1 = cls.env['res.partner'].create({'name': 'Company 1', 'is_company': True})
        cls.company_2 = cls.env['res.partner'].create({'name': 'Company 2', 'is_company': True})

        cls.contact_1_email = 'test1@localhost'
        cls.contact_1 = cls.env['res.partner'].create({
            'name': 'Contact 1',
            'is_company': False,
            'email': cls.contact_1_email,
            'parent_id': cls.company_1.id,
        })

    def _run_partner_change_wizard(self, contact, destination_company=None):
        wizard = self.env['res.partner.change.parent'].with_context({
            'active_id': contact.id,
            'active_model': 'res.partner',
        }).create({
            'new_company_id': destination_company.id if destination_company else None,
        })
        wizard.validate()
        return wizard.new_contact_id

    def test_new_contact_is_not_the_old_contact(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        self.assertEqual(len(new_contact), 1)
        self.assertNotEqual(new_contact, self.contact_1)

    def test_email_propagation_to_new_contact(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        self.assertEqual(new_contact.email, self.contact_1_email)

    def test_old_contact_is_archived(self):
        self._run_partner_change_wizard(self.contact_1, self.company_2)
        self.assertFalse(self.contact_1.active)

    def test_new_contact_has_destination_parent(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        self.assertEqual(new_contact.parent_id, self.company_2)

    def test_old_contact_is_still_under_the_original_parent(self):
        self._run_partner_change_wizard(self.contact_1, self.company_2)
        self.assertEqual(self.contact_1.parent_id, self.company_1)

    def test_no_destination_parent(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, None)
        self.assertFalse(new_contact.parent_id)

    def test_no_source_parent(self):
        contact_with_no_company = self.env['res.partner'].create({
            'name': 'Contact With No Company',
            'is_company': False,
            'email': 'test2@localhost',
            'parent_id': False,
        })
        new_contact = self._run_partner_change_wizard(contact_with_no_company, self.company_1)
        self.assertEqual(new_contact.parent_id, self.company_1)
