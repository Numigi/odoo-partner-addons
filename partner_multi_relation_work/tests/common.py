# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.api import Environment
from odoo.tests import common


class PartnerRelationCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(PartnerRelationCase, cls).setUpClass()

        cls.admin = cls.env.ref('base.user_root')
        cls.demo_user = cls.env.ref('base.user_demo')

        # Run all tests with a non-admin user to prevent missing sudo() statements.
        cls.env = Environment(cls.env.cr, cls.env.uid, {})

        cls.company_1 = cls.env['res.partner'].create({'name': 'Company 1', 'is_company': True})
        cls.company_2 = cls.env['res.partner'].create({'name': 'Company 2', 'is_company': True})
        cls.company_3 = cls.env['res.partner'].create({'name': 'Company 3', 'is_company': True})

        cls.contact_1 = cls.env['res.partner'].create({
            'name': 'Contact 1',
            'is_company': False,
            'email': 'test1@localhost',
            'parent_id': cls.company_1.id,
        })

        cls.contact_2 = cls.env['res.partner'].create({
            'name': 'Contact 2',
            'is_company': False,
            'email': 'test2@localhost',
            'parent_id': cls.company_2.id,
        })

        cls.contact_3 = cls.env['res.partner'].create({
            'name': 'Contact 3',
            'is_company': False,
            'email': 'test3@localhost',
            'parent_id': cls.company_3.id,
        })

        cls.relation_type_work = cls.env.ref('partner_multi_relation_work.relation_type_work')
        cls.relation_type_same = cls.env.ref('partner_multi_relation_work.relation_type_same')

        cls.customer_type = cls.env['res.partner.relation.type'].create({
            'name': 'is customer of',
            'name_inverse': 'has customer',
        })

        cls.father_type = cls.env['res.partner.relation.type'].create({
            'name': 'is the father of',
            'name_inverse': 'is the children of',
        })

    def setUp(self):
        super().setUp()
        self._add_new_relation(self.contact_1, self.contact_2, self.father_type)
        self._add_new_relation(self.contact_1, self.company_3, self.customer_type)

    def _add_new_relation(self, left_partner, right_partner, relation_type, user=None):
        return self.env['res.partner.relation'].sudo(user=user or self.demo_user).create({
            'left_partner_id': left_partner.id,
            'right_partner_id': right_partner.id,
            'type_id': relation_type.id,
            'date_start': datetime.now(),
        })

    def _find_and_verify_single_relation(self, left_partner, right_partner, relation_type):
        """Find a single relation of a given type between 2 partners.

        Verify that there is one and only one relation for the given parameters.

        :param left_partner: the left partner in the relation
        :param right_partner: the right partner in the relation
        :param relation_type: the type of relation to search for
        :return: a record of res.partner.relation.all
        """
        relation = self.env['res.partner.relation.all'].with_context(active_test=True).search([
            ('this_partner_id', '=', left_partner.id),
            ('other_partner_id', '=', right_partner.id),
            ('type_selection_id.type_id', '=', relation_type.id),
        ])
        self.assertEqual(
            len(relation), 1,
            'Expected one relation of type {relation_type} between '
            '{left_partner} and {right_partner}.'
            .format(left_partner=left_partner.display_name,
                    right_partner=right_partner.display_name,
                    relation_type=relation_type.display_name))
        return relation
