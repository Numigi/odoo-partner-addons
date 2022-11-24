# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ForwardSortationAera(models.Model):

    _name = 'forward.sortation.area'
    _description = 'Forward Sorting Area'

    name = fields.Char('Name', required=True)
    sector = fields.Char('Sector')
    province = fields.Char('Province')
    latitude = fields.Char('Latitude')
    longitude = fields.Char('Longitude')
    active = fields.Boolean('Active', default=True)

    territory_ids = fields.Many2many(
        'res.territory', 'res_territory_fsa_rel', 'fsa_id', 'territory_id',
        string='Territories')

    partner_ids = fields.One2many('res.partner', 'fsa_id', string='Partners')

    def write(self, vals):
        res = super(ForwardSortationAera, self).write(vals)
        if 'name' in vals:
            self.mapped('partner_ids')._compute_fsa_id()
            self.env['res.partner'].search([
                ('zip', 'ilike', vals['name'] + '%'),
            ])._compute_fsa_id()

        return res
