# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models


class ResPartnerDuplicateField(models.Model):

    _name = 'res.partner.duplicate.field'
    _description = 'Partner Duplicate Field'

    field_id = fields.Many2one(
        'ir.model.fields', string='Partner Field', required=True, domain=[
            ('model', '=', 'res.partner'),
            ('ttype', 'not in', ('many2many', 'one2many')),
            ('related', '=', False),
            ('compute', '=', False),
        ], help=_(
            'You can only select fields which are not many2many, '
            'one2many, related and computed.')
    )
    technical_name = fields.Char(
        'Technical name', related='field_id.name', readonly=True)
    name = fields.Char(
        'Name', related='field_id.field_description', readonly=True)
    type = fields.Selection('Type', related='field_id.ttype', readonly=True)

    sequence = fields.Integer('Sequence')
