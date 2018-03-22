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
        'res.partner', string='Preserved Partner',
        track_visibility='onchange')
    partner_archived_id = fields.Many2one(
        'res.partner', string='Archived Partner',
        compute='_compute_partner_archived_id')

    merge_line_ids = fields.One2many(
        'res.partner.merge.line', 'duplicate_id', string='Merge Lines')

    merger_reason_id = fields.Many2one(
        'merger.reason', string='Merger Reason')

    warning_message = fields.Char()

    state = fields.Selection(
        string='State',
        selection=[
            ('to_validate', 'To Validate'),
            ('resolved', 'Resolved (Not Duplicate)'),
            ('merged', 'Merged'),
        ], default='to_validate',
        track_visibility='onchange',
    )

    @api.depends('partner_1_id', 'partner_2_id', 'partner_preserved_id')
    def _compute_partner_archived_id(self):
        for rec in self.filtered(lambda r: r.partner_preserved_id):
            rec.partner_archived_id = (
                rec.partner_2_id
                if rec.partner_preserved_id == rec.partner_1_id
                else rec.partner_1_id
            )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._update_partner_order()
        return res

    def _update_partner_order(self):
        """Update the order of the partners on the duplicate record.

        The left partner (partner_1_id) must be the partner with the lower id.
        """
        duplicates_in_wrong_order = (d for d in self if d.partner_1_id.id > d.partner_2_id.id)
        for duplicate in duplicates_in_wrong_order:
            duplicate.write({
                'partner_1_id': duplicate.partner_2_id.id,
                'partner_2_id': duplicate.partner_1_id.id,
            })

    @api.onchange('partner_preserved_id')
    def onchange_partner_preserved_id(self):
        if not self.partner_preserved_id:
            return

        partner_1_preserved = (
            self.partner_preserved_id == self.partner_1_id)
        for line in self.merge_line_ids:
            line.partner_1_selected = partner_1_preserved
            line.partner_2_selected = not partner_1_preserved

        partners = self.partner_1_id | self.partner_2_id
        partner_to_archive = partners - self.partner_preserved_id
        if (
            not self.partner_preserved_id.is_company and
            not partner_to_archive.is_company and
            self.env['account.move'].sudo().search([
                ('partner_id', '=', partner_to_archive.id)
            ])
        ):
            self.warning_message = (_(
                "Please note that the contact %(src)s is linked to journal "
                "entries. By merging it with %(dst)s, all the accounting "
                "history of %(src)s will be moved under %(dst)s.") % {
                'src': partner_to_archive.name,
                'dst': self.partner_preserved_id.name,
            })
        else:
            self.warning_message = ""

    def _update_preserved_partner(self):
        vals = {}
        for line in self.merge_line_ids:
            field_name = line.duplicate_field_id.technical_name
            partner = False

            if (
                self.partner_preserved_id == self.partner_1_id and
                line.partner_2_selected
            ):
                partner = self.partner_2_id

            if (
                self.partner_preserved_id == self.partner_2_id and
                line.partner_1_selected
            ):
                partner = self.partner_1_id

            if partner:
                field_value = partner._get_field_value(field_name)
                if field_value:
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
        self._update_preserved_partner()

        # Call the method _merge of the crm partner merge widget
        partners = self.partner_1_id | self.partner_2_id
        base_wizard = self.env['base.partner.merge.automatic.wizard']
        base_wizard._merge(partners.ids, self.partner_preserved_id)

        # Archive the partner which is not preserved
        partner_to_archive = partners - self.partner_preserved_id
        partner_to_archive.write({'active': False})

        # Add messages to the chatter
        self._log_archived_partner_message()
        self._log_preserved_partner_message()

        # Change duplicate state
        self.write({'state': 'merged'})

        # Resolve all other duplicates linked to the partner archived
        self.search([
            '|',
            ('partner_1_id', '=', partner_to_archive.id),
            ('partner_2_id', '=', partner_to_archive.id),
            ('state', '=', 'to_validate')
        ]).action_resolve()

        return self.partner_preserved_id.get_formview_action()

    def _log_archived_partner_message(self):
        """Log the message in the mail thread of the archived partner."""
        message = _('Merged into {partner}.').format(partner=self.partner_preserved_id.display_name)
        self.partner_archived_id.message_post(body=message)

    def _log_preserved_partner_message(self):
        """Log the message in the mail thread of the preserved partner."""
        message = _('Merged with {partner}.').format(partner=self.partner_archived_id.display_name)

        if self.merger_reason_id:
            reason = _("The merger reason is: {reason}.").format(reason=self.merger_reason_id.name)
            message = '{message}\n\n{reason}'.format(message=message, reason=reason)

        self.partner_preserved_id.message_post(body=message)

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

        duplicates = []
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

            duplicates += cr.fetchall()

        return duplicates

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
