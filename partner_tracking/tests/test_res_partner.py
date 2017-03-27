# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests import TransactionCase


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()

        self.partner = self.env['res.partner'].create({
             'name': 'Partner Test',
        })

        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testlogin',
            'email': 'test@test.com',
        })

    def test_state_switching(self):
        self.test_user.partner_id.state = 'controlled'
        ctx = {'action': self.env.ref('base.action_res_users_my').id}
        self.test_user.sudo(self.test_user).with_context(params=ctx).write({
            'email': 'changetest@test.com',
        })  # test the case of the user updating his preferences
        self.assertEqual(self.test_user.partner_id.state, 'controlled')
        self.assertEqual(self.partner.state, 'controlled')
        self.partner.sudo(self.test_user).write({
            'name': 'Partner Name Change Test',
        })  # test the case in which the user is not in the validation group
        self.assertEqual(self.partner.state, 'pending')
        self.partner.action_set_controlled()
        self.assertEqual(self.partner.state, 'controlled')
        self.env.ref(
            'partner_tracking.group_partner_validation'
        ).users = [(4, self.test_user.id)]
        self.partner.sudo(self.test_user).write({
            'name': 'Partner Name Change Test 2',
        })  # test the case in which the user is in the validation group
        self.assertEqual(self.partner.state, 'controlled')
