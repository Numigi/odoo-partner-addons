# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import PartnerRelationCase


class TestResPartner(PartnerRelationCase):

    def test_auto_create_work_relation_with_parent(self):
        self._find_and_verify_single_relation(
            self.contact_1, self.company_1, self.relation_type_work)

    def test_if_partner_is_company__no_relation_created_with_parent(self):
        new_company = self.env['res.partner'].create({
            'name': 'Company 1',
            'is_company': True,
            'parent_id': self.company_1.id,
        })

        relation = self.env['res.partner.relation.all'].search([
            ('this_partner_id', '=', new_company.id),
            ('other_partner_id', '=', self.company_1.id),
            ('type_selection_id.type_id', '=', self.relation_type_work.id),
        ])

        assert not relation
