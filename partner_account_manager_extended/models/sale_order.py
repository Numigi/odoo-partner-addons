# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    account_manager_id = fields.Many2one(
        related="partner_id.account_manager_id", string="Manager", store=True
    )
