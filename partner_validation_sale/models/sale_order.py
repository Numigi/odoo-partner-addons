# -*- coding: utf-8 -*-
# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, _
from odoo.exceptions import Warning as WarningOdoo


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        restricted_partners = self.mapped('partner_id.commercial_partner_id'). \
            filtered(lambda p: p.customer_state != 'approved'). \
            mapped('display_name')
        if restricted_partners:
            raise WarningOdoo(_("The client ​%s has to be approved"
                                " in order to confirm this sale order.") % (",".join(restricted_partners)))
        return super().action_confirm()
