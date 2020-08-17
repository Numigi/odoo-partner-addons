# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResTerritory(models.Model):

    _name = 'res.territory'
    _description = 'Territory'

    name = fields.Char('Name', required=True)

    fsa_ids = fields.Many2many(
        'forward.sortation.area',
        'res_territory_fsa_rel', 'territory_id', 'fsa_id',
        string='FSA')

    partner_ids = fields.Many2many(
        string='Partners',
        comodel_name='res.partner',
        relation='rel_territory_partner')

    color = fields.Integer('Color Index')
    active = fields.Boolean('Active', default=True)
