# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.territory_1 = cls.env['res.territory'].create({
            'name': 'Territory 1',
        })
        cls.territory_2 = cls.env['res.territory'].create({
            'name': 'Territory 2',
        })

        cls.fsa_1 = cls.env['forward.sortation.area'].create({
            'name': 'A1A',
            'territory_ids': [(6, 0, [
                cls.territory_1.id, cls.territory_2.id])],
        })
        cls.fsa_2 = cls.env['forward.sortation.area'].create({
            'name': 'A1B',
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner',
            'zip': 'A1AB2B',
        })

        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Partner',
            'zip': 'A1CB2B',
        })

    def test_compute_fsa_id(self):
        self.assertEqual(self.partner.fsa_id, self.fsa_1)
        self.assertFalse(self.partner_2.fsa_id)

        self.partner.write({'zip': None})
        self.assertFalse(self.partner.fsa_id)
        self.assertFalse(self.partner_2.fsa_id)

    def test_field_related_territory_ids(self):
        self.assertIn(self.territory_1, self.partner.territory_ids)
        self.assertIn(self.territory_2, self.partner.territory_ids)

        self.fsa_1.write({'territory_ids': [(3, self.territory_1.id)]})
        self.assertNotIn(self.territory_1, self.partner.territory_ids)
        self.assertIn(self.territory_2, self.partner.territory_ids)

        self.territory_1.write({
            'fsa_ids': [(6, 0, [
                self.fsa_1.id, self.fsa_2.id])]
        })
        self.assertIn(self.territory_1, self.partner.territory_ids)
        self.assertIn(self.territory_2, self.partner.territory_ids)

    def test_change_fsa_name_change_partners(self):
        self.assertEqual(self.partner.fsa_id, self.fsa_1)
        self.assertIn(self.partner, self.fsa_1.partner_ids)

        self.fsa_1.write({'name': 'A1C'})
        self.assertFalse(self.partner.fsa_id)
        self.assertEqual(self.partner_2.fsa_id, self.fsa_1)
