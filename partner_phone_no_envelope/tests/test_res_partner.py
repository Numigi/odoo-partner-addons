# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestPartnerWithEnvelopeHidden(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Partner 1'})

    def test_if_no_parameter_then_envelope_is_hidden(self):
        self.env['ir.config_parameter'].search(
            [('key', '=', 'partner_phone_no_envelope.hide_envelope')]).unlink()
        self.assertTrue(self.partner.phone_envelope_hidden)

    def test_if_parameter_is_true_then_envelope_is_hidden(self):
        self.env['ir.config_parameter'].set_param(
            'partner_phone_no_envelope.hide_envelope', 'True')
        self.assertTrue(self.partner.phone_envelope_hidden)

    def test_if_parameter_is_false_then_envelope_is_not_hidden(self):
        self.env['ir.config_parameter'].set_param(
            'partner_phone_no_envelope.hide_envelope', 'False')
        self.assertFalse(self.partner.phone_envelope_hidden)

    def test_if_parameter_is_0_then_envelope_is_not_hidden(self):
        self.env['ir.config_parameter'].set_param(
            'partner_phone_no_envelope.hide_envelope', '0')
        self.assertFalse(self.partner.phone_envelope_hidden)
