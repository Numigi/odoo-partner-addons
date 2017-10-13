# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRelationStrength(models.Model):

    _name = 'res.partner.relation.strength'
    _description = 'Partner Relation Strength'

    name = fields.Char(
        'Name',
        required=True,
    )

    sequence = fields.Integer(
        'Sequence',
    )
