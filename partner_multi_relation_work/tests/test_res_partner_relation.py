# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import AccessError
from .common import PartnerRelationCase
from odoo.tests.common import users


class TestResPartnerRelationTypeSameRelation(PartnerRelationCase):

    @users('demo')
    def test_create_same_person_relation_by_non_admin(self):
        with self.assertRaises(AccessError):
            self._add_new_relation(self.contact_1, self.contact_2, self.relation_type_same)

    def test_create_same_person_relation_by_admin(self):
        self._add_new_relation(
            self.contact_1, self.contact_2, self.relation_type_same)

    def test_delete_same_person_relation_by_non_admin(self):
        relation = self._add_new_relation(
            self.contact_1, self.contact_2, self.relation_type_same)

        with self.assertRaises(AccessError):
            relation.with_user(self.demo_user.id).unlink()

    def test_delete_same_person_relation_by_admin(self):
        relation = self._add_new_relation(
            self.contact_1, self.contact_2, self.relation_type_same)
        relation.sudo().unlink()

    def test_modify_same_person_relation_by_non_admin(self):
        relation = self._add_new_relation(
            self.contact_1, self.contact_2, self.relation_type_same)

        with self.assertRaises(AccessError):
            relation.with_user(self.demo_user.id).right_partner_id = self.contact_3

    def test_modify_same_person_relation_by_admin(self):
        relation = self._add_new_relation(
            self.contact_1, self.contact_2, self.relation_type_same)
        relation.sudo().right_partner_id = self.contact_3
