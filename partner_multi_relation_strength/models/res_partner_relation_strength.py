# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRelationStrength(models.Model):

    _name = 'res.partner.relation.strength'
    _description = 'Partner Relation Strength'

    _order = 'sequence'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence')
