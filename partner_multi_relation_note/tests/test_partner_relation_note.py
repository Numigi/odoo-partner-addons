# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestPartnerRelationNote(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.child = cls.env['res.partner'].create({'name': 'Contact 1'})

        cls.father = cls.env['res.partner'].create({
            'name': 'Father of Contact 1',
        })

        cls.father_type = cls.env['res.partner.relation.type'].sudo().create({
            'name': 'is the father of',
            'name_inverse': 'is the children of',
        })

        cls.note = 'This is a note'

        cls.father_relation = cls.env['res.partner.relation.all'].create({
            'this_partner_id': cls.father.id,
            'other_partner_id': cls.child.id,
            'type_id': cls.father_type.id,
            'note': cls.note,
        })

        cls.child_relation = cls.env['res.partner.relation.all'].search([
            ('this_partner_id', '=', cls.child.id),
            ('other_partner_id', '=', cls.father.id),
            ('type_id', '=', cls.father_type.id),
        ])

    def test_on_create_note_is_propagated_to_inverse_relations(self):
        self.assertEqual(self.father_relation.note, self.note)
        self.assertEqual(self.child_relation.note, self.note)

    def test_when_update_note_on_relation_then_update_inverse_relation(self):
        new_note = 'This is another note'
        self.father_relation.note = new_note
        self.father_relation.refresh()
        self.assertEqual(self.father_relation.note, new_note)
        self.assertEqual(self.child_relation.note, new_note)
