# -*- coding: utf-8 -*-
# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, _
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        restricted_partners = self.mapped('partner_id.commercial_partner_id').\
            filtered(lambda p: p.customer and p.customer_state != 'approved').\
            mapped('name')
        if restricted_partners:
            raise Warning(_("The client ​%s has to be approved"
                            " in order to confirm this sale order." % str(restricted_partners)))
        return super(SaleOrder, self).action_confirm()
