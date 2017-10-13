# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.partner_model = cls.env['res.partner']
        cls.type_model = cls.env['res.partner.relation.type']

        cls.company = cls.partner_model.create({
            'name': 'test company',
            'is_company': True,
        })

    def test_onchange_parent_id(self):
        partner = self.partner_model.create({
            'name': 'Test no work relation',
            'parent_id': self.company.id,
        })
        self.assertFalse(partner.parent_id)

    def test_create(self):
        self.type_model.create({
            'name': 'works for',
            'name_inverse': 'has employee',
            'is_work_relation': True,
        })
        partner = self.partner_model.create({
            'name': 'Test create',
            'parent_id': self.company.id,
        })
        self.assertEqual(len(partner.relation_all_ids), 1)
