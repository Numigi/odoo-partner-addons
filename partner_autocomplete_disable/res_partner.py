# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ResPartnerAutocompleteDisable(models.Model):
    _inherit = "res.partner"

    @api.model
    def autocomplete(self, query):
        return []
