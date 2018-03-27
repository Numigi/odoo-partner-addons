# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
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

        cls.work_relation_type = cls.env.ref(
            'partner_multi_relation_extended.relation_type_work')

    def test_01_onchange_parent_id(self):
        self.work_relation_type.is_work_relation = False
        partner = self.partner_model.create({
            'name': 'Test no work relation',
            'parent_id': self.company.id,
        })
        self.assertFalse(partner.parent_id)

    def test_02_create(self):
        partner = self.partner_model.create({
            'name': 'Test create',
            'parent_id': self.company.id,
        })
        self.assertEqual(len(partner.relation_all_ids), 1)
