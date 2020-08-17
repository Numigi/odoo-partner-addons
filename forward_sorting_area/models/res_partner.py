# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartnerWithFSA(models.Model):

    _inherit = 'res.partner'

    fsa_id = fields.Many2one(
        'forward.sortation.area', string='FSA',
        compute='_compute_fsa_id', store=True)

    territory_ids = fields.Many2many(
        'res.territory', string='Territories', related='fsa_id.territory_ids',
        readonly=True)

    @api.depends('zip')
    def _compute_fsa_id(self):
        areas = {
            a.name.lower(): a for a in
            self.env['forward.sortation.area'].search([])
        }
        for record in self:
            if record.zip:
                record.fsa_id = areas.get(record.zip[0:3].lower(), None)
            else:
                record.fsa_id = None
