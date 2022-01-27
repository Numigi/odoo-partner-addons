# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange(
        'name', 'parent_id', 'company_type', 'is_company', 'lastname', 'firstname'
    )
    def _onchange_name_find_duplicates(self):
        if self.lastname and self.firstname:
            return super(ResPartner, self)._onchange_name_find_duplicates()
        return
