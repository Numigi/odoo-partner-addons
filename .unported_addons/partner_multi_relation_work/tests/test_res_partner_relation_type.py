# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestResPartnerRelationTypeSamePerson(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.relation_type = self.env.ref('partner_multi_relation_work.relation_type_same')

    def test_setting_contact_left_to_company_on_same_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'contact_type_left': 'c'})

    def test_setting_not_symmetric_on_same_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'is_symmetric': False})

    def test_setting_allow_self_on_same_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'allow_self': True})

    def test_allowing_invalid_onchange_on_same_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'handle_invalid_onchange': 'ignore'})


class TestResPartnerRelationTypeWork(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.relation_type = self.env.ref('partner_multi_relation_work.relation_type_work')

    def test_setting_contact_left_to_company_on_work_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'contact_type_left': 'c'})

    def test_setting_contact_right_to_person_on_work_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'contact_type_right': 'p'})

    def test_setting_symmetric_on_work_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'is_symmetric': True})

    def test_setting_allow_self_on_work_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'allow_self': True})

    def test_allowing_invalid_onchange_on_work_relation_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.relation_type.write({'handle_invalid_onchange': 'ignore'})
