# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.company = cls.env['res.partner'].create({
            'name': 'Toyota',
            'company_type': 'company',
        })
        cls.person = cls.env['res.partner'].create({
            'name': 'John Doe',
            'company_type': 'person',
        })
        cls.type_inc = cls.env['res.partner.business.type'].create({
            'name': 'Inc.',
            'shortcut': 'Inc.',
        })

    def test_remove_title(self):
        self.person.name = 'Dr. John Doe'
        self.person.refresh()
        self.assertEqual(self.person.name, 'John Doe')

    def test_remove_title_with_space_before(self):
        self.person.name = ' Dr. John Doe'
        self.person.refresh()
        self.assertEqual(self.person.name, 'John Doe')

    def test_remove_title_with_no_leading_dot(self):
        self.person.name = 'Dr John Doe'
        self.person.refresh()
        self.assertEqual(self.person.name, 'John Doe')

    def test_remove_title_with_upper_case(self):
        self.person.name = 'DR. John Doe'
        self.person.refresh()
        self.assertEqual(self.person.name, 'John Doe')

    def test_remove_translated_title(self):
        self.translation_mr = self.env['ir.translation'].create({
            'lang': 'fr_CA',
            'name': 'res.partner.title,shortcut',
            'type': 'model',
            'src': 'Mr.',
            'value': 'M.',
            'res_id': self.env.ref('base.res_partner_title_mister').id
        })

        self.person.name = 'M. John Doe'
        self.person.refresh()
        self.assertEqual(self.person.name, 'John Doe')

    def test_remove_business_type(self):
        self.company.name = 'Toyota Inc.'
        self.company.refresh()
        self.assertEqual(self.company.name, 'Toyota')

    def test_remove_business_type_with_space_after(self):
        self.company.name = 'Toyota Inc. '
        self.company.refresh()
        self.assertEqual(self.company.name, 'Toyota')

    def test_remove_business_type_with_no_leading_dot(self):
        self.company.name = 'Toyota Inc'
        self.company.refresh()
        self.assertEqual(self.company.name, 'Toyota')

    def test_remove_business_type_with_upper_case(self):
        self.company.name = 'Toyota INC.'
        self.company.refresh()
        self.assertEqual(self.company.name, 'Toyota')

    def test_remove_translated_business_type(self):
        self.translation_inc = self.env['ir.translation'].create({
            'lang': 'fr_CA',
            'name': 'res.partner.business.type,shortcut',
            'type': 'model',
            'src': 'Inc.',
            'value': 'Inc.tr',
            'res_id': self.type_inc.id
        })

        self.company.name = 'Toyota Inc.tr'
        self.company.refresh()
        self.assertEqual(self.company.name, 'Toyota')
