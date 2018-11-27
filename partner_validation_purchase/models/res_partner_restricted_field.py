# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRestrictedField(models.Model):
    _inherit = 'res.partner.restricted.field'

    apply_on_purchases = fields.Boolean('Apply on purchases', default=False)
