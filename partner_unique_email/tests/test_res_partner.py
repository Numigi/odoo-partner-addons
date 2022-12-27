# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.exceptions import UserError, ValidationError


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.email = 'test_unique_email@localhost'
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner',
            'email': cls.email,
        })

    def test_partner_with_same_email_constraint(self):
        with self.assertRaises(ValidationError):
            self.env['res.partner'].create({
                'name': 'Other Partner',
                'email': self.email,
            })

    def test_partner_with_same_email_onchange(self):
        partner = self.env['res.partner'].create({'name': 'Other Partner'})

        with self.env.do_in_onchange():
            partner.email = self.email

            with self.assertRaises(UserError):
                partner._onchange_email_check_partners_with_same_email()
