# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRelation(models.Model):

    _inherit = 'res.partner.relation'

    strength = fields.Many2one(
        'Strength',
        comodel_name='res.partner.relation.strength',
    )

    note = fields.Char(
        'Note',
        help='Use this field to add information about the relation. For '
             'example, if the relation is "Belongs to the professional order",'
             ' you can put here the professional order number.',
    )
