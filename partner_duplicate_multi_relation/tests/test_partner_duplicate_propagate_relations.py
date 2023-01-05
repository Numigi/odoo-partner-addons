# -*- coding: utf-8 -*-
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.api import Environment
from odoo.tests import common


class TestPartnerDuplicatePropagateRelations(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Run all tests with a non-admin user to prevent missing sudo() statements.
        cls.env = Environment(cls.env.cr, cls.env.ref('base.user_demo').id, {})

        cls.contact_1 = cls.env['res.partner'].create({'name': 'Contact 1'})
        cls.contact_1_duplicate = cls.env['res.partner'].create({'name': 'Contact 1'})

        cls.father = cls.env['res.partner'].create({
            'name': 'Father of Contact 1',
        })

        cls.employer = cls.env['res.partner'].create({
            'name': 'Old Employer',
        })

        cls.father_type = cls.env['res.partner.relation.type'].sudo().create({
            'name': 'is the father of',
            'name_inverse': 'is the children of',
        })

        cls.employer_type = cls.env['res.partner.relation.type'].sudo().create({
            'name': 'is the employer of',
            'name_inverse': 'is the employee of',
        })

        cls.father_relation = cls.env['res.partner.relation'].create({
            'type_id': cls.father_type.id,
            'left_partner_id': cls.father.id,
            'right_partner_id': cls.contact_1_duplicate.id,
        })

        cls.employer_relation = cls.env['res.partner.relation'].create({
            'type_id': cls.employer_type.id,
            'left_partner_id': cls.contact_1_duplicate.id,
            'right_partner_id': cls.employer.id,
        })

        cls.duplicate_line = cls.env['res.partner.duplicate'].search([
            ('partner_1_id', '=', cls.contact_1.id),
            ('partner_2_id', '=', cls.contact_1_duplicate.id),
        ])
        cls.duplicate_line.partner_preserved_id = cls.contact_1
        cls.duplicate_line.open_partner_merge_wizard()
        cls.duplicate_line._onchange_auto_select_preserved_partner()

    def test_relations_are_propagated_if_not_exist_on_preserved_partner(self):
        """Test that the relations are propagated if they do not exist on the preserved partner."""
        self.duplicate_line.merge_partners()

        self.father_relation.refresh()
        self.employer_relation.refresh()

        self.assertEqual(self.father_relation.right_partner_id, self.contact_1)
        self.assertEqual(self.employer_relation.left_partner_id, self.contact_1)

    def test_relations_are_deleted_if_exist_on_preserved_partner(self):
        """Test that the relations are deleted if they exist on the preserved partner."""
        self.env['res.partner.relation'].create({
            'type_id': self.father_type.id,
            'left_partner_id': self.father.id,
            'right_partner_id': self.contact_1.id,
        })

        self.env['res.partner.relation'].create({
            'type_id': self.employer_type.id,
            'left_partner_id': self.contact_1.id,
            'right_partner_id': self.employer.id,
        })

        self.duplicate_line.merge_partners()

        self.assertFalse(self.father_relation.exists())
        self.assertFalse(self.employer_relation.exists())
