# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class ResPartnerMergeLine(models.Model):

    _name = 'res.partner.merge.line'
    _description = 'Merger Line'

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

    @api.onchange('partner_1_selected')
    def onchange_partner_1_selected(self):
        self.partner_2_selected = not self.partner_1_selected

    @api.onchange('partner_2_selected')
    def onchange_partner_2_selected(self):
        self.partner_1_selected = not self.partner_2_selected
