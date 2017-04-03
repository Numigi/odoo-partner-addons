# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests import SavepointCase
from openerp.exceptions import Warning


class TestResPartner(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.normal_user = cls.env['res.users'].create({
            'name': 'Normal User',
            'login': 'normaluserlogin',
            'email': 'normaluser@test.com',
        })

        cls.controller_user = cls.env['res.users'].create({
            'name': 'Controller User',
            'login': 'controlleruserlogin',
            'email': 'controlleruser@test.com',
            'groups_id': [(4, cls.env.ref(
                'partner_tracking.group_partner_validation'
            ).id)],
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner Test',
        })

        cls.normal_user_partner = cls.normal_user.partner_id

    def test_01_write_updating_preferences(self):
        """
        Test the case of the user changing his preferences.
        """
        self.normal_user_partner.state = 'controlled'
        self.assertEqual(self.normal_user_partner.state, 'controlled')
        ctx = {'action': self.env.ref('base.action_res_users_my').id}
        self.normal_user.sudo(self.normal_user).with_context(params=ctx).write(
            {'email': 'changetest@test.com'}
        )
        self.assertEqual(self.normal_user_partner.state, 'controlled')

    def test_02_write_normal_user(self):
        """
        Test the case of a user that is not part of the validation group
        updating a partner and trying to change the state of a partner.
        """
        self.assertEqual(self.partner.state, 'controlled')
        self.partner.sudo(self.normal_user).write({
            'name': 'Partner Name Change Test',
        })
        self.assertEqual(self.partner.state, 'pending')
        with self.assertRaises(Warning):
            self.partner.sudo(self.normal_user).state = 'controlled'

    def test_03_write_controller_user(self):
        """
        Test the case of user that is part of the validation group updating a
        partner and validating a partner.
        """
        self.assertEqual(self.partner.state, 'controlled')
        self.partner.sudo(self.controller_user).write({
            'name': 'Partner Name Change Test 2',
        })
        self.assertEqual(self.partner.state, 'controlled')
        self.partner.state = 'pending'
        self.assertEqual(self.partner.state, 'pending')
        self.partner.sudo(self.controller_user).state = 'controlled'
        self.assertEqual(self.partner.state, 'controlled')

    def test_04_create_normal_user(self):
        """
        Test the case of a user that is not part of the validation group
        and creates a partner.
        """
        partner = self.env['res.partner'].sudo(self.normal_user).create({
            'name': 'Partner Name Change Test',
            'state': 'controlled',
        })
        self.assertEqual(partner.state, 'pending')
