# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from .common import PartnerRelationCase


class TestResPartnerChangeParent(PartnerRelationCase):

    def _run_partner_change_wizard(self, contact, destination_company=None):
        wizard = self.env['res.partner.change.parent'].with_context({
            'active_id': contact.id,
            'active_model': 'res.partner',
        }).create({
            'new_company_id': destination_company.id if destination_company else None,
        })
        wizard.validate()
        return wizard.new_contact_id

    def test_same_person_relation_added_between_old_and_new_contact(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        self._find_single_relation(self.contact_1, new_contact, self.relation_type_same)

    def test_propagation_of_old_relations_to_new_contact(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        self._find_single_relation(new_contact, self.contact_2, self.father_type)
        self._find_single_relation(new_contact, self.company_3, self.customer_type)

    def test_work_relation_added_between_new_contact_and_destination_company(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        self._find_single_relation(new_contact, self.company_2, self.relation_type_work)

    def test_work_relation_between_new_contact_and_source_company(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        relation = self._find_single_relation(new_contact, self.company_1, self.relation_type_work)
        self.assertEqual(relation.date_end, fields.Date.context_today(self.contact_1))

    def test_same_person_after_multiple_parent_change(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        new_contact_2 = self._run_partner_change_wizard(new_contact, self.company_3)
        self._find_single_relation(new_contact_2, self.contact_1, self.relation_type_same)
        self._find_single_relation(new_contact_2, new_contact, self.relation_type_same)
        self._find_single_relation(self.contact_1, new_contact, self.relation_type_same)

    def test_work_relations_after_multiple_parent_change(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        new_contact_2 = self._run_partner_change_wizard(new_contact, self.company_3)
        self._find_single_relation(new_contact_2, self.company_1, self.relation_type_work)
        self._find_single_relation(new_contact_2, self.company_2, self.relation_type_work)
        self._find_single_relation(new_contact_2, self.company_3, self.relation_type_work)
