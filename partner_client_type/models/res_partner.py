# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    client_type_ids = fields.Many2many(
        "client.type",
        "res_partner_client_rel",
        "partner_id",
        "client_id",
        string="Client Type",
    )

    @api.model
    def _commercial_fields(self):
        res = super()._commercial_fields()
        res.append("client_type_ids")
        return res
