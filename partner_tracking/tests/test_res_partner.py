# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests import SavepointCase
from openerp import fields, SUPERUSER_ID
import time
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

        cls.partner_tracking_write_date = cls.partner.tracking_write_date

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

    def test_05_timestamp_normal_user(self):
        """
        Test the update of tracking_write_uid and tracking_write_date when a
        normal user modifies partners.
        """
        self.assertTrue(self.partner_tracking_write_date)
        self.assertEqual(
            self.partner.tracking_write_date, self.partner_tracking_write_date
        )
        time.sleep(2)
        timestamp = fields.Datetime.now()
        self.partner.sudo(self.normal_user).write({
            'name': 'Partner Name Change Test',
        })
        self.assertTrue(
            self.partner_tracking_write_date < timestamp
            <= self.partner.tracking_write_date <= fields.Datetime.now()
        )
        self.assertEqual(self.partner.tracking_write_uid, self.normal_user)

    def test_06_timestamp_admin(self):
        """
        Test the update of tracking_write_uid and tracking_write_date when the
        admin modifies partners. Both fields must be updated only if the admin
        changes the state of the partner.
        """
        self.partner.sudo(self.normal_user).write({
            'name': 'Partner Name Change Test',
        })
        self.assertEqual(self.partner.tracking_write_uid, self.normal_user)
        write_date = self.partner.tracking_write_date
        time.sleep(2)
        # not changing the state
        self.partner.write({
            'name': 'Partner Name Change Test 2',
        })
        self.assertEqual(self.partner.tracking_write_uid, self.normal_user)
        self.assertEqual(self.partner.tracking_write_date, write_date)
        # changing the state
        state = 'pending' if self.partner.state == 'controlled' else 'pending'
        self.partner.write({
            'state': state
        })
        self.assertEqual(self.partner.tracking_write_uid.id, SUPERUSER_ID)
        self.assertTrue(write_date < self.partner.tracking_write_date)
