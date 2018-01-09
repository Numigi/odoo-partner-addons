# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class ResPartnerMergeLine(models.Model):

    _name = 'res.partner.merge.line'
    _description = __doc__

    duplicate_id = fields.Many2one(
        'res.partner.duplicate', ondelete='cascade', required=True)
    duplicate_field_id = fields.Many2one(
        'res.partner.duplicate.field', 'Field')
    partner_preserved_id = fields.Many2one(
        'res.partner', related='duplicate_id.partner_preserved_id')
    partner_1_value = fields.Char('Partner 1 Value')
    partner_1_selected = fields.Boolean('Preserved')
    partner_2_value = fields.Char('Partner 2 Value')
    partner_2_selected = fields.Boolean('Preserved')

    def create_merge_lines(self, duplicate):
        lines = self
        duplicate_fields = self.env['res.partner.duplicate.field'].search([])
        partner_1 = duplicate.partner_1_id
        partner_2 = duplicate.partner_2_id

        for duplicate_field in duplicate_fields:
            field = partner_1._fields[duplicate_field.technical_name]
            partner_1_value = field.convert_to_display_name(
                getattr(partner_1, duplicate_field.technical_name),
                partner_1)
            partner_2_value = field.convert_to_display_name(
                getattr(partner_2, duplicate_field.technical_name),
                partner_2)

            lines |= self.create({
                'duplicate_id': duplicate.id,
                'duplicate_field_id': duplicate_field.id,
                'partner_1_value': partner_1_value,
                'partner_2_value': partner_2_value,
            })
        return lines

    @api.onchange('partner_1_selected')
    def onchange_partner_1_selected(self):
        self.partner_2_selected = not self.partner_1_selected

    @api.onchange('partner_2_selected')
    def onchange_partner_2_selected(self):
        self.partner_1_selected = not self.partner_2_selected
