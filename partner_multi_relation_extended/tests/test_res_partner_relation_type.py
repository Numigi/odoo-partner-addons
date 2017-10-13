# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestResPartnerRelationType(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerRelationType, cls).setUpClass()
        cls.type_model = cls.env['res.partner.relation.type']

        cls.work_relation_type = cls.type_model.create({
            'name': 'works for',
            'name_inverse': 'has employee',
            'is_work_relation': True,
        })

    def test_onchange_is_work_relation(self):
        self.work_relation_type._onchange_is_work_relation()
        self.assertEqual(self.work_relation_type.contact_type_left, 'p')
        self.assertEqual(self.work_relation_type.contact_type_right, 'c')

    def test_check_is_work_relation(self):
        with self.assertRaises(ValidationError):
            self.type_model.create({
                'name': 'works also for',
                'name_inverse': 'also has employee',
                'is_work_relation': True,
            })
        self.assertEqual(self.work_relation_type.contact_type_left, 'p')
        self.assertEqual(self.work_relation_type.contact_type_right, 'c')
