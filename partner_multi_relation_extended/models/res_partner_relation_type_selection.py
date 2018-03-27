# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ResPartnerRelationTypeSelection(models.Model):

    _inherit = 'res.partner.relation.type.selection'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Override the original method to filter the results by active type.
        """
        return self.search(
            [
                '|',
                ('type_id.name', operator, name),
                ('type_id.name_inverse', operator, name),
                ('type_id.active', '=', True),
            ] + (args or []),
            limit=limit
        ).name_get()
