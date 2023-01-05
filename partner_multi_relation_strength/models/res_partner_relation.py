# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRelationWithStrength(models.Model):

    _inherit = 'res.partner.relation'

    strength_id = fields.Many2one(
        'res.partner.relation.strength',
        'Strength',
        ondelete='restrict',
    )
