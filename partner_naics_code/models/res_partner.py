# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    naics_code_id = fields.Many2one("partner.naics.code", string="NAICS Code")
