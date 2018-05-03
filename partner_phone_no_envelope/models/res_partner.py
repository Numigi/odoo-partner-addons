# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PartnerWithEnvelopeHidden(models.Model):

    _inherit = 'res.partner'

    phone_envelope_hidden = fields.Boolean(
        'Phone Envelope Hidden',
        compute='_compute_phone_envelope_hidden',
    )

    def _compute_phone_envelope_hidden(self):
        phone_envelope_hidden = self.env['ir.config_parameter'].sudo().get_param(
            'partner_phone_no_envelope.hide_envelope', True)

        for partner in self:
            partner.phone_envelope_hidden = phone_envelope_hidden not in ('False', '0')
