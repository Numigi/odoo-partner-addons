# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestResPartnerRelationType(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerRelationType, cls).setUpClass()
        cls.type_model = cls.env['res.partner.relation.type']
        cls.type_selection_model = cls.env[
            'res.partner.relation.type.selection']
        cls.partner_model = cls.env['res.partner']
        cls.relation_model = cls.env['res.partner.relation']

        cls.relation_type_same = cls.env.ref(
            'partner_multi_relation_extended.relation_type_same')

        cls.work_relation_type = cls.env.ref(
            'partner_multi_relation_extended.relation_type_work')

        cls.work_relation_type_selection = cls.type_selection_model.search([
            ('type_id', '=', cls.work_relation_type.id),
            ('name', '=', 'Works for'),
        ])

        cls.contact = cls.partner_model.create({
            'name': 'Test contact',
            'is_company': False,
        })

        cls.company = cls.partner_model.create({
            'name': 'Test company',
            'is_company': True,
        })

    def test_01_onchange_is_work_relation(self):
        self.work_relation_type._onchange_is_work_relation()
        self.assertEqual(self.work_relation_type.contact_type_left, 'p')
        self.assertEqual(self.work_relation_type.contact_type_right, 'c')

    def test_02_check_is_work_relation(self):
        with self.assertRaises(ValidationError):
            self.type_model.create({
                'name': 'works also for',
                'name_inverse': 'also has employee',
                'is_work_relation': True,
            })
        self.assertEqual(self.work_relation_type.contact_type_left, 'p')
        self.assertEqual(self.work_relation_type.contact_type_right, 'c')

    def test_03_check_work_relation_creation(self):
        """
        Test that the user cannot create a partner relation (all) with a work
        relation type. If so, the field type_selection_id is emptied, so we
        test that it raises an IntegrityError as this field is required.
        """
        work_relation = self.env['res.partner.relation.all'].create({
            'this_partner_id': self.contact.id,
            'other_partner_id': self.company.id,
            'type_selection_id': self.work_relation_type_selection.id,
        })
        with self.assertRaises(IntegrityError):
            work_relation.onchange_type_selection_id()

    def test_04_unlink(self):
        """
        Test that the relation type identified as 'same' cannot be deleted
        """
        with self.assertRaises(ValidationError):
            self.relation_type_same.unlink()
        not_same = self.type_model.create({
            'name': 'Test delete not same',
            'name_inverse': 'Test delete not same',
        })
        not_same.unlink()
