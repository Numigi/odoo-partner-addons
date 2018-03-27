# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestResPartnerRelationTypeSelection(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerRelationTypeSelection, cls).setUpClass()
        cls.type_model = cls.env['res.partner.relation.type']
        cls.type_selection_model = cls.env[
            'res.partner.relation.type.selection']

        cls.type = cls.type_model.create({
            'name': 'Type Test',
            'name_inverse': 'Type Inverse Test',
        })

        cls.type_selection = cls.type_selection_model.search([
            ('type_id', '=', cls.type.id),
            ('name', '=', 'Type Test'),
        ])

        cls.type_selection_name = (
            cls.type_selection.id, cls.type_selection.name)

    def test_01_name_search_type_active(self):
        res = self.type_selection_model.name_search()
        self.assertIn(self.type_selection_name, res)

    def test_02_name_search_type_inactive(self):
        self.type.write({'active': False})
        res = self.type_selection_model.name_search()
        self.assertNotIn(self.type_selection_name, res)
