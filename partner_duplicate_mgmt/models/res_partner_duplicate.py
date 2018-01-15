# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartnerDuplicate(models.Model):

    _name = 'res.partner.duplicate'
    _description = 'Partner Duplicate'
    _inherit = ['mail.thread']

    partner_1_id = fields.Many2one(
        'res.partner', string='Partner 1', readonly=True)
    partner_2_id = fields.Many2one(
        'res.partner', string='Partner 2', readonly=True)
    partner_preserved_id = fields.Many2one(
        'res.partner', string='Partner Preserved',
        track_visibility='onchange')
    merge_line_ids = fields.One2many(
        'res.partner.merge.line', 'duplicate_id', string='Merge Lines')

    merger_reason_id = fields.Many2one(
        'merger.reason', string='Merger Reason')

    warning_message = fields.Char(compute='_compute_warning_message')

    state = fields.Selection(
        string='State',
        selection=[
            ('to_validate', 'To Validate'),
            ('resolved', 'Resolved (Not Duplicate)'),
            ('merged', 'Merged'),
        ], default='to_validate',
        track_visibility='onchange',
    )

    @api.onchange('partner_preserved_id')
    def onchange_partner_preserved_id(self):
        if not self.partner_preserved_id:
            return

        partner_1_preserved = (
            self.partner_preserved_id == self.partner_1_id)
        for line in self.merge_line_ids:
            line.partner_1_selected = partner_1_preserved
            line.partner_2_selected = not partner_1_preserved

    @api.multi
    @api.depends('partner_preserved_id')
    def _compute_warning_message(self):
        for record in self:
            record.warning_message = ""

            partner_1_moves = self.env['account.move'].search([
                ('partner_id', '=', record.partner_1_id.id)
            ])
            partner_2_moves = self.env['account.move'].search([
                ('partner_id', '=', record.partner_2_id.id)
            ])
            src_partners = self.env['res.partner']

            if (
                partner_1_moves and (
                    not record.partner_preserved_id or
                    record.partner_preserved_id == record.partner_2_id)
            ):
                src_partners = record.partner_1_id

            if (
                partner_2_moves and (
                    not record.partner_preserved_id or
                    record.partner_preserved_id == record.partner_1_id)
            ):
                src_partners |= record.partner_2_id

            if src_partners:
                if len(src_partners) == 1:
                    message = (_(
                        "Please note that the partner %(src)s is linked "
                        "to journal entries. ") % {
                        'src': src_partners.name,
                    })
                else:
                    message = (_(
                        "Please note that the partners %(src)s are linked "
                        "to journal entries. ") % {
                        'src': ', '.join(src_partners.mapped('name')),
                    })
                record.warning_message = (
                    message + _(
                        "By merging a partner X with a "
                        "partner Y, all the accounting history of the "
                        "partner X will be moved under the partner Y."))

    def update_preserved_partner(self):
        vals = {}
        for line in self.merge_line_ids:
            field_name = line.duplicate_field_id.technical_name
            field_value = False

            if (
                self.partner_preserved_id == self.partner_1_id and
                line.partner_2_selected
            ):
                field_value = line.partner_2_value

            if (
                self.partner_preserved_id == self.partner_2_id and
                line.partner_1_selected
            ):
                field_value = line.partner_1_value

            if field_value:
                if line.duplicate_field_id.type == 'many2one':
                    field_value = getattr(self.partner_2_id, field_name).id
                vals[field_name] = field_value

        self.partner_preserved_id.write(vals)

    def merge_partners(self):
        # Verify that a partner is checked for all lines
        for line in self.merge_line_ids:
            if not line.partner_1_selected and not line.partner_2_selected:
                raise UserError(_(
                    'Please select a value to preserve for the field %s.') %
                    (line.duplicate_field_id.name))

        # Update preserved partner fields values
        self.update_preserved_partner()

        # Call the method _merge of the crm partner merge widget
        partners = self.partner_1_id | self.partner_2_id
        base_wizard = self.env['base.partner.merge.automatic.wizard']
        base_wizard._merge(partners.ids, self.partner_preserved_id)

        # Archive the partner which is not preserved
        partner_to_archive = partners - self.partner_preserved_id
        partner_to_archive.write({'active': False})

        # Add messages to the chatter
        message_src = _('Merged into %s') % (self.partner_preserved_id.name)
        partner_to_archive.message_post(body=message_src)

        message_reason = ""
        if self.merger_reason_id:
            message_reason = _(
                " Merger reason is : %s.") % (self.merger_reason_id.name,)

        message_dst = _('Merged with %s.') % (partner_to_archive.name,)
        self.partner_preserved_id.message_post(
            body=(message_dst + message_reason))

        # Change duplicate state
        self.write({'state': 'merged'})

        view = self.env.ref('partner_duplicate_mgmt.view_partner_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_id': self.partner_preserved_id.id,
        }

    def _find_partner_duplicates(self):
        criteria = []
        similarity_1 = self.env['ir.config_parameter'].get_param(
            'partner_duplicate_mgmt.partner_name_similarity_1')
        criteria.append((similarity_1, 0, 9))

        similarity_2 = self.env['ir.config_parameter'].get_param(
            'partner_duplicate_mgmt.partner_name_similarity_2')
        criteria.append((similarity_2, 10, 17))

        similarity_3 = self.env['ir.config_parameter'].get_param(
            'partner_duplicate_mgmt.partner_name_similarity_3')
        criteria.append((similarity_3, 18, 100))

        cr = self.env.cr
        for criterion in criteria:
            cr.execute('SELECT set_limit(%s)', (criterion[0],))
            cr.execute("""
                SELECT p1.id, p2.id
                FROM res_partner p1
                JOIN res_partner p2 ON p1.indexed_name %% p2.indexed_name
                WHERE p1.id != p2.id
                AND p1.company_type = p2.company_type
                AND ((p1.parent_id IS NOT DISTINCT FROM p2.parent_id)
                  OR (p1.parent_id IS NULL AND p1.id != p2.parent_id)
                  OR (p2.parent_id IS NULL AND p2.id != p1.parent_id)
                )
                AND length(p1.indexed_name)
                    BETWEEN %(min_length)s AND %(max_length)s
                AND NOT EXISTS (
                    SELECT NULL
                    FROM res_partner_duplicate d
                    WHERE (d.partner_1_id = p1.id AND d.partner_2_id = p2.id)
                    OR    (d.partner_1_id = p2.id AND d.partner_2_id = p1.id)
                )
            """, {
                'min_length': criterion[1],
                'max_length': criterion[2],
            })

        return cr.fetchall()

    def create_duplicates(self):
        res = self._find_partner_duplicates()
        duplicates_sorted = [tuple(sorted(r)) for r in res]
        duplicates = list(set(duplicates_sorted))

        for dup in duplicates:
            self.create({'partner_1_id': dup[0], 'partner_2_id': dup[1]})

    @api.multi
    def action_resolve(self):
        self.filtered(
            lambda x: x.state == 'to_validate').write({
                'state': 'resolved'})

        for record in self:
            message = _('The duplicate line (%s, %s) is resolved.') % (
                record.partner_1_id.name, record.partner_2_id.name)
            record.partner_1_id.message_post(body=message)
            record.partner_2_id.message_post(body=message)

    @api.multi
    def set_to_draft(self):
        self.write({'state': 'to_validate'})

    @api.multi
    def open_partner_merge_wizard(self):
        if len(self) > 1:
            raise UserError(_("Please, select only one duplicate."))

        if self.state != 'to_validate':
            raise UserError(_(
                "You can not merge a line which is not to validate."))

        merge_lines = (
            self.env['res.partner.merge.line'].create_merge_lines(self))
        self.write({'merge_line_ids': [(6, 0, merge_lines.ids)]})

        view = self.env.ref(
            'partner_duplicate_mgmt.res_partner_merge_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'target': 'new',
            'res_id': self.id,
        }
