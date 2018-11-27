# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import SavepointCase
from psycopg2 import IntegrityError


class TestResPartnerRestrictedField(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerRestrictedField, cls).setUpClass()

    def test_01_create_double_restricted_field(self):
        """
        Test the case of creating two restricted fields on the same partner field.
        """
        partner_phone_field_id = self.env.ref('base.field_res_partner_phone').id

        vals = {
            'field_id': partner_phone_field_id
        }
        self.env['res.partner.restricted.field'].create(vals)
        with self.assertRaises(IntegrityError):
            self.env['res.partner.restricted.field'].create(vals)
