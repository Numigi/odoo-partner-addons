# -*- coding: utf-8 -*-
# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, _
from odoo.exceptions import Warning as WarningOdoo


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        outgoings = self.filtered(
            lambda sp: (sp.picking_type_code == 'outgoing' and
                        sp.location_dest_id.usage == 'customer'))
        if outgoings:
            restricted_partners = self.mapped('partner_id.commercial_partner_id'). \
                filtered(lambda p: p.customer_state != 'approved'). \
                mapped('display_name')

            if restricted_partners:
                raise WarningOdoo(_("The partner %s has to be approved in order"
                                    " to confirm this stock move.") % (",".join(restricted_partners)))
        return super().button_validate()
