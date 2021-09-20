# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    client_type_ids = fields.Many2many(
        "client.type",
        "res_partner_client_rel",
        "partner_id",
        "client_id",
        string="Client Type",
    )
