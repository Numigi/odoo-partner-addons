# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests import TransactionCase


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()

        self.PartnerObj = self.env['res.partner']

        self.partner = self.PartnerObj.create({
             'name': 'Partner Test',
        })

    def test_state_switching(self):
        self.assertEqual(self.partner.state, 'controlled')
        self.env.ref('partner_tracking.group_partner_validation').users = False
        self.partner.write({
            'name': 'Partner Name Change Test',
        })
        self.assertEqual(self.partner.state, 'pending')
        self.partner.action_set_controlled()
        self.assertEqual(self.partner.state, 'controlled')
