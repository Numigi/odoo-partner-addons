# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from itertools import product
from ddt import ddt, data, unpack
from odoo.tests import common


PHONE_NUMBERS = [
    # (Given Phone, Formatted Phone)
    (False, False),
    ('418 666-6666', '+1 418-666-6666'),
    ('418 666-6666, ext 123', '+1 418-666-6666 ext. 123'),
]

PHONE_FIELDS = ('phone', 'mobile')

PHONE_CASES = product(PHONE_NUMBERS, PHONE_FIELDS)


@ddt
class TestPhoneFormatOnSave(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'John Doe',
            'country_id': cls.env.ref('base.ca').id,
        })

    @data(*PHONE_CASES)
    @unpack
    def test_on_write__phone_formatted(self, phones, field):
        given_phone, expected_phone = phones
        self.partner[field] = given_phone
        self.partner.refresh()
        assert self.partner[field] == expected_phone

    @data(*PHONE_CASES)
    @unpack
    def test_on_create__phone_formatted(self, phones, field):
        given_phone, expected_phone = phones
        new_partner = self.partner.copy({field: given_phone})
        assert new_partner[field] == expected_phone
