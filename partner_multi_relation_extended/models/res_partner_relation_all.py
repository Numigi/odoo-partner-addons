# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ResPartnerRelationAll(models.AbstractModel):

    _inherit = 'res.partner.relation.all'

    strength = fields.Many2one(
        string='Strength',
        comodel_name='res.partner.relation.strength',
    )

    note = fields.Char(
        'Note',
        help='Use this field to add information about the relation. For '
             'example, if the relation is "Belongs to the professional order",'
             ' you can put here the professional order number.',
    )

    @api.model_cr_context
    def _auto_init(self):
        """Add new fields to auto_init."""
        def add_additional_view_field(field):
            if field not in self._additional_view_fields:
                self._additional_view_fields.append(field)

        add_additional_view_field('strength')
        add_additional_view_field('note')

        return super(ResPartnerRelationAll, self)._auto_init()
