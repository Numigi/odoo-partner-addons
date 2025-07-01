# copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def get_read_access_actions(self):
        res = super().get_read_access_actions()
        additional_actions = [
            "action_view_sale_order",
        ]
        res.extend(additional_actions)
        return res
