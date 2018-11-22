# -*- coding: utf-8 -*-
# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, _
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        restricted_partners = self.mapped('partner_id.commercial_partner_id').\
            filtered(lambda p: p.supplier and p.supplier_state != 'approved').\
            mapped('name')
        if restricted_partners:
            raise Warning(_("The supplier ​%s has to be approved"
                            " in order to confirm this purchase order." % str(restricted_partners)))
        return super(PurchaseOrder, self).button_confirm()
