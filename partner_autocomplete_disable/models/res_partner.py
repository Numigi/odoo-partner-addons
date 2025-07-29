# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ResPartnerAutocompleteDisable(models.Model):
    _inherit = "res.partner"

    @api.model
    def _rpc_remote_api(self, *args, **kwargs):
        return {}, False
