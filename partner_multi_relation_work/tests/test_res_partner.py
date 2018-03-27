# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import PartnerRelationCase


class TestResPartner(PartnerRelationCase):

    def test_auto_create_work_relation_with_parent(self):
        self._find_single_relation(self.contact_1, self.company_1, self.relation_type_work)
