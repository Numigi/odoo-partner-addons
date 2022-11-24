# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class Partner(models.Model):

    _inherit = "res.partner"

    account_manager_id = fields.Many2one("res.users")

    @api.model
    def _commercial_fields(self):
        res = super()._commercial_fields()
        res.append("account_manager_id")
        return res
