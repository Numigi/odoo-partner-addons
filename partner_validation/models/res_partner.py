# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import threading
from odoo import api, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _should_check_partner_validation(self):
        is_testing = getattr(threading.currentThread(), "testing", False)
        return not is_testing or self._context.get("testing_partner_validation")
