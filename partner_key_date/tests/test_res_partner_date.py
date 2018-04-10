# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz

from datetime import datetime
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests import common
from odoo.exceptions import UserError

_NOW = datetime.now(pytz.utc)
_2_YEARS_AGO = _NOW - relativedelta(years=2)
_18_MONTHS_AGO = _NOW.now() - relativedelta(months=18)
_4_MONTHS_AGO = _NOW.now() - relativedelta(months=4)
_1_YEAR_LATER = _NOW.now() + relativedelta(years=1)


class TestResPartnerDate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.user.tz = 'Canada/Eastern'

        cls.partner = cls.env['res.partner'].create({
            'name': 'My Partner',
            'email': 'partner_test@email',
        })

        cls.date_type_1 = cls.env['res.partner.date.type'].create({
            'name': 'Birthday',
        })
        cls.date_type_2 = cls.env['res.partner.date.type'].create({
            'name': 'Founding Date',
        })
        cls.date_type_3 = cls.env['res.partner.date.type'].create({
            'name': 'Opening Date',
        })

        cls.partner_date_1 = cls.env['res.partner.date'].create({
            'date_type_id': cls.date_type_1.id,
            'partner_id': cls.partner.id,
            'date': _2_YEARS_AGO,
        })
        cls.partner_date_2 = cls.env['res.partner.date'].create({
            'date_type_id': cls.date_type_2.id,
            'partner_id': cls.partner.id,
            'date': _18_MONTHS_AGO,
        })
        cls.partner_date_3 = cls.env['res.partner.date'].create({
            'date_type_id': cls.date_type_3.id,
            'partner_id': cls.partner.id,
            'date': _4_MONTHS_AGO,
        })
        cls.template = cls.env.ref('partner_key_date.anniversary_email_template')

    def test_compute_age(self):
        self.assertAlmostEqual(self.partner_date_1.age, 2, 2)
        self.assertAlmostEqual(self.partner_date_2.age, 1.5, 2)
        self.assertAlmostEqual(self.partner_date_3.age, 0.3, 2)

    @freeze_time(_1_YEAR_LATER)
    def test_compute_age_for_all_dates(self):
        self.env['res.partner.date'].compute_age_for_all_dates()
        self.assertAlmostEqual(self.partner_date_1.age, 3, 2)
        self.assertAlmostEqual(self.partner_date_2.age, 2.5, 2)
        self.assertAlmostEqual(self.partner_date_3.age, 1.3, 2)

    def test_send_anniversary_email(self):
        self.partner_date_1.write({
            'date': _2_YEARS_AGO.astimezone(pytz.timezone('Canada/Eastern')),
            'diffusion': True,
        })
        self.env['res.partner.date'].send_anniversary_emails()
        mail = self.env['mail.mail'].search([
            ('email_to', '=', self.partner.email),
            ('subject', '=', self.template.subject),
        ])
        self.assertIn(self.partner.name, mail.body)

    def test_send_anniversary_with_no_email(self):
        self.partner.email = None
        self.partner_date_1.write({
            'date': _2_YEARS_AGO.astimezone(pytz.timezone('Canada/Eastern')),
            'diffusion': True,
        })
        with self.assertRaises(UserError):
            self.env['res.partner.date'].send_anniversary_emails()
