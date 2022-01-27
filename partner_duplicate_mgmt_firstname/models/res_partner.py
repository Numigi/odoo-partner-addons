# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models
from odoo.addons.partner_duplicate_mgmt.models.res_partner import UPDATE_DUPLICATES_FIELDS


UPDATE_DUPLICATES_FIELDS.update(("firstname", "lastname"))


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange(*UPDATE_DUPLICATES_FIELDS)
    def _onchange_name_find_duplicates(self):
        if self.lastname and self.firstname:
            return super()._onchange_name_find_duplicates()
