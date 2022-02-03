# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ddt import ddt, data
from freezegun import freeze_time

from odoo.tests import common
from odoo.exceptions import UserError

def as_canada_estern(date):
    return date.astimezone(pytz.timezone('Canada/Eastern'))

_NOW = as_canada_estern(datetime.now(pytz.utc))
_2_YEARS_AGO = _NOW - relativedelta(years=2)
_18_MONTHS_AGO = _NOW.now() - relativedelta(months=18)
_4_MONTHS_AGO = _NOW.now() - relativedelta(months=4)
_1_YEAR_LATER = _NOW.now() + relativedelta(years=1)


@ddt
class TestResPartnerDate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.user.tz = 'Canada/Eastern'

        cls.partner = cls.env['res.partner'].create({
            'name': 'My Partner',
            'email': 'partner_test@email',
        })

        cls.template = cls.env.ref('partner_key_date.anniversary_email_template')

        cls.date_type_1 = cls.env['res.partner.date.type'].create({
            'name': 'Birthday',
            'mail_template_id': cls.template.id,
        })
        cls.date_type_2 = cls.env['res.partner.date.type'].create({
            'name': 'Founding Date',
            'mail_template_id': cls.template.id,
        })
        cls.date_type_3 = cls.env['res.partner.date.type'].create({
            'name': 'Opening Date',
            'mail_template_id': cls.template.id,
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

    def test_compute_age(self):
        assert round(self.partner_date_1.age, 2) == 2
        assert round(self.partner_date_2.age, 2) == 1.5
        assert round(self.partner_date_3.age, 2) == 0.3

    @freeze_time(_1_YEAR_LATER)
    def test_compute_age_for_all_dates(self):
        self.env['res.partner.date'].compute_age_for_all_dates()
        assert round(self.partner_date_1.age, 2) == 3
        assert round(self.partner_date_2.age, 2) == 2.5
        assert round(self.partner_date_3.age, 2) == 1.3

    def _find_sent_email(self):
        return self.env['mail.mail'].search([
            ('email_to', '=', self.partner.email),
            ('subject', '=', self.template.subject),
        ])

    def test_send_anniversary_email(self):
        self.partner_date_1.write({
            'date': _2_YEARS_AGO,
            'diffusion': True,
        })
        self.env['res.partner.date'].send_anniversary_emails()
        mail = self._find_sent_email()
        assert mail
        assert self.partner.name in mail.body

    def test_find_anniversary_dates(self):
        self.partner_date_1.write({
            'date': _2_YEARS_AGO,
            'diffusion': True,
        })
        result = self.env['res.partner.date']._find_anniversary_dates()
        assert self.partner_date_1 in result

    def test_find_anniversary_dates__with_delta(self):
        self.date_type_1.diffusion_delta = 4
        self.partner_date_1.write({
            'date': _2_YEARS_AGO + timedelta(4),
            'diffusion': True,
        })
        result = self.env['res.partner.date']._find_anniversary_dates()
        assert self.partner_date_1 in result

    @data(1, -1)
    def test_find_anniversary_date__not_found(self, number_of_days):
        self.partner_date_1.write({
            'date': _2_YEARS_AGO + timedelta(number_of_days),
            'diffusion': True,
        })
        result = self.env['res.partner.date']._find_anniversary_dates()
        assert self.partner_date_1 not in result

    def test_if_no_email_on_partner_then_no_mail_sent(self):
        self.partner.email = None
        self.partner_date_1.write({
            'date': _2_YEARS_AGO,
            'diffusion': True,
        })
        self.env['res.partner.date'].send_anniversary_emails()
        mail = self._find_sent_email()
        assert not mail

    def test_if_no_mail_template_defined_on_key_date_then_no_mail_sent(self):
        self.partner_date_1.write({
            'date': _2_YEARS_AGO,
            'diffusion': True,
        })
        self.date_type_1.mail_template_id = False
        self.env['res.partner.date'].send_anniversary_emails()
        mail = self._find_sent_email()
        assert not mail
