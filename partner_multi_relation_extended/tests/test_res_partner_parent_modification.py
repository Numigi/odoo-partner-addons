# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import common


class TestResPartnerParentModification(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerParentModification, cls).setUpClass()
        cls.partner_model = cls.env['res.partner']
        cls.relation_model = cls.env['res.partner.relation']
        cls.relation_all_model = cls.env['res.partner.relation.all']
        cls.type_model = cls.env['res.partner.relation.type']
        cls.wizard_model = cls.env['res.partner.parent.modification']

        cls.today = fields.Date.today()

        cls.individuals = [cls.partner_model.create({
            'name': 'Test individual %s' % i,
            'is_company': False,
            'email': 'test%s@email',
        }) for i in range(2)]

        cls.companies = [cls.partner_model.create({
            'name': 'Test Company %s' % i,
            'is_company': True,
        }) for i in range(3)]

        cls.work_relation_type = cls.env.ref(
            'partner_multi_relation_extended.rel_type_work')

        cls.customer_type = cls.type_model.create({
            'name': 'is customer of',
            'name_inverse': 'has customer',
        })

        cls.accountant_type = cls.type_model.create({
            'name': 'has accountant',
            'name_inverse': 'is accountant',
        })

        cls.relation_type_same = cls.env.ref(
            'partner_multi_relation_extended.rel_type_same')

        cls.relations = [cls.relation_model.create({
            'left_partner_id': record[0].id,
            'right_partner_id': record[1].id,
            'type_id': record[2].id,
            'date_start': cls.today,
        }) for record in [
            (cls.individuals[0], cls.individuals[1], cls.accountant_type),
            (cls.individuals[0], cls.companies[0], cls.work_relation_type),
            (cls.individuals[1], cls.companies[1], cls.work_relation_type),
            (cls.individuals[0], cls.companies[2], cls.customer_type),
        ]]

    def test_01_validate(self):
        """
        Test standard parent modification
        """
        contact = self.individuals[0]
        new_company = self.companies[1]
        former_relations = self.env['res.partner.relation.all'].search([
            ('this_partner_id', '=', contact.id),
            ('is_automatic', '=', False),
            ('type_selection_id.type_id.is_work_relation', '=', False),
            '|', ('active', '=', False), ('active', '=', True)
        ])
        wizard = self.wizard_model.with_context({
            'active_id': contact.id,
            'active_model': 'res.partner',
        }).create({
            'new_company_id': new_company.id,
        })
        wizard.validate()
        new_contact = self.partner_model.search([
            ('name', '=', contact.name),
            ('parent_id', '=', new_company.id),
        ])
        self.assertEqual(
            len(new_contact), 1,
            'There should be a new contact with the same name and the new '
            'company as parent.')
        self.assertFalse(
            contact.email,
            'The former contact should have lost his email.')
        self.assertEqual(
            new_contact.email,
            'test%s@email',
            'The new contact should have the email of the former contact.')
        relation_same = self.relation_all_model.search([
            ('this_partner_id', '=', contact.id),
            ('other_partner_id', '=', new_contact.id),
            ('type_selection_id.type_id', '=', self.relation_type_same.id),
        ])
        self.assertEqual(
            len(relation_same), 1,
            'There should be a new relation saying that the former contact '
            'and the new one are the same person.')
        new_work_relation = self.relation_all_model.search([
            ('this_partner_id', '=', new_contact.id),
            ('other_partner_id', '=', new_company.id),
            ('type_selection_id.type_id', '=', self.work_relation_type.id),
        ])
        self.assertEqual(
            len(new_work_relation), 1,
            'There should be a new relation saying that the new contact '
            'works for the new company.')
        for relation in former_relations:
            self.assertEqual(
                relation.this_partner_id, new_contact,
                'All former relations should have been transferred on the new'
                'contact.')
        self.assertFalse(
            contact.active,
            'The former contact should be archived.')

    def test_02_several_parent_modifications(self):
        """
        Test that same person relations are kept when changing the parent
        multiple times
        """
        first_contact = self.individuals[0]
        second_company = self.companies[1]
        wizard = self.wizard_model.with_context({
            'active_id': first_contact.id,
            'active_model': 'res.partner',
        }).create({
            'new_company_id': second_company.id,
        })
        wizard.validate()
        second_contact = self.partner_model.search([
            ('name', '=', first_contact.name),
            ('parent_id', '=', second_company.id),
        ])
        third_company = self.companies[2]
        wizard = self.wizard_model.with_context({
            'active_id': second_contact.id,
            'active_model': 'res.partner',
        }).create({
            'new_company_id': third_company.id,
        })
        wizard.validate()
        third_contact = self.partner_model.search([
            ('name', '=', second_contact.name),
            ('parent_id', '=', third_company.id),
        ])
        third_same_as_second = self.relation_all_model.search([
            ('this_partner_id', '=', third_contact.id),
            ('other_partner_id', '=', second_contact.id),
            ('type_selection_id.type_id', '=', self.relation_type_same.id),
        ])
        third_same_as_first = self.relation_all_model.search([
            ('this_partner_id', '=', third_contact.id),
            ('other_partner_id', '=', first_contact.id),
            ('type_selection_id.type_id', '=', self.relation_type_same.id),
        ])
        self.assertEqual(
            len(third_same_as_second), 1,
            'There should be a relation saying that the third contact is the '
            'same as the second one.'
        )
        self.assertEqual(
            len(third_same_as_first), 1,
            'There should also be a relation saying that the third contact is '
            'the same as the first one.'
        )

    def test_03_validate_no_work_relation_type(self):
        """
        Test that wizard can't operate the modification when there isn't
        any work relation type
        """
        self.work_relation_type.is_work_relation = False
        wizard = self.wizard_model.with_context({
            'active_id': self.individuals[0].id,
            'active_model': 'res.partner',
        }).create({
            'new_company_id': self.companies[1].id,
        })
        with self.assertRaises(ValidationError):
            wizard.validate()

    def test_04_access_rights_automatic_relation(self):
        """
        Test that only the administrator can update a partner relation
        which is automatic
        """
        contact = self.individuals[0]
        new_company = self.companies[1]
        wizard = self.wizard_model.with_context({
            'active_id': contact.id,
            'active_model': 'res.partner',
        }).create({
            'new_company_id': new_company.id,
        })
        wizard.validate()
        new_contact = self.partner_model.search([
            ('name', '=', contact.name),
            ('parent_id', '=', new_company.id),
        ])
        relation_same = self.relation_all_model.search([
            ('this_partner_id', '=', contact.id),
            ('other_partner_id', '=', new_contact.id),
            ('type_selection_id.type_id', '=', self.relation_type_same.id),
        ])
        demo_user_id = self.env.ref('base.user_demo').id
        with self.assertRaises(AccessError):
            relation_same.sudo(demo_user_id).note = 'test note from demo'
        with self.assertRaises(AccessError):
            relation_same.sudo(demo_user_id).unlink()
        relation_same.note = 'test note from admin'
        relation_same.unlink()
