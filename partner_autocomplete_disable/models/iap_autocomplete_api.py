# © 2024 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, models


class IapAutocompleteEnrichAPI(models.AbstractModel):
    _inherit = "iap.autocomplete.api"

    @api.model
    def _contact_iap(self, local_endpoint, action, params, timeout=15):
        return []
