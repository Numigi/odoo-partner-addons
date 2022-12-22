# © 2017-2018 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartnerDuplicate(models.Model):
    """A model reprensenting a combination of 2 duplicate partners."""

    _name = 'res.partner.duplicate'
    _description = 'Partner Duplicate'
    _inherit = ['mail.thread']

    partner_1_id = fields.Many2one(
        'res.partner', string='Partner 1', readonly=True)
    partner_2_id = fields.Many2one(
        'res.partner', string='Partner 2', readonly=True)
    partner_preserved_id = fields.Many2one(
        'res.partner', string='Preserved Partner',
        tracking=True)
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
        tracking=True,
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
    def _onchange_auto_select_preserved_partner(self):
        """Automatically select the preserved partner for all field lines."""
        if not self.partner_preserved_id:
            return

        partner_1_preserved = self.partner_preserved_id == self.partner_1_id
        for line in self.merge_line_ids:
            line.partner_1_selected = partner_1_preserved
            line.partner_2_selected = not partner_1_preserved

    @api.onchange('partner_preserved_id')
    def _onchange_check_contacts_with_journal_entries(self):
        """Check for contacts with journal entries.

        Contacts are partners that are not companies (people or addresses).

        When 2 contacts are merged together, every table rows linked to
        the archived contact are changed to point on the preserved contact.
        This includes journal entries, invoices, payments, etc.

        When merging 2 contacts, the user must be warned because this operation
        is not reversible.
        """
        both_partners_are_contacts = (
            self.partner_preserved_id and
            self.partner_archived_id and
            not self.partner_preserved_id.is_company and
            not self.partner_archived_id.is_company
        )

        def partner_has_journal_entries(partner):
            """Verify whether a partner has journal entries or not.

            :return True if the partner has journal entries, False otherwise.
            """
            if not partner:
                return False
            return self.env['account.move'].sudo().search(
                [('partner_id', '=', partner.id)], count=True)

        if both_partners_are_contacts and partner_has_journal_entries(self.partner_archived_id):
            self.warning_message = _(
                "Please note that the contact {archived_partner} is linked to journal "
                "entries. By merging it with {preserved_partner}, all the accounting "
                "history of {archived_partner} will be moved under {preserved_partner}.").format(
                archived_partner=self.partner_archived_id.name,
                preserved_partner=self.partner_preserved_id.name,
            )
        else:
            self.warning_message = ""

    def _update_preserved_partner(self):
        """Update field values on the preserved partner.

        If the email is copied from the archived partner to the preserved partner,
        then, we remove the email from the archived partner.
        """
        vals = self._get_values_to_write_on_preserved_partner()

        # Prevent having 2 partners with the same email.
        if vals.get('email') == self.partner_archived_id.email:
            self.partner_archived_id.email = None

        self.partner_preserved_id.write(vals)

    def _get_values_to_write_on_preserved_partner(self):
        """Get the values to write on the preserved partner.

        All field values selected on the archived partner are written to
        the preserved partner.

        Values selected on the preserved partner are ignored.

        :return: a dict of field values
        """
        vals = {}

        partner_1_preserved = self.partner_preserved_id == self.partner_1_id
        partner_2_preserved = self.partner_preserved_id == self.partner_2_id

        for line in self.merge_line_ids:
            field_name = line.duplicate_field_id.technical_name

            if partner_1_preserved and line.partner_2_selected:
                vals[field_name] = self.partner_2_id._get_field_value(field_name)

            elif partner_2_preserved and line.partner_1_selected:
                vals[field_name] = self.partner_1_id._get_field_value(field_name)

        return vals

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

    def _find_duplicate_partner_ids(self):
        """Find all combinations of 2 partners that match as duplicates.

        :return: list of tuples containing partner ids (i.e. [(1, 2), (1, 3), ...])
        """
        criteria = []
        similarity_1 = self._get_partner_name_similarity(1)
        criteria.append((similarity_1, 0, 9))

        similarity_2 = self._get_partner_name_similarity(2)
        criteria.append((similarity_2, 10, 17))

        similarity_3 = self._get_partner_name_similarity(3)
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

    def _get_partner_name_similarity(self, level):
        """Get the floor similarity for the given similarity level.

        The sudo is required because since Odoo 11.0, config parameters are
        only readable by the admin group.

        :param level: the similarity level from 1 to 3
        :return: the floor similarity limit
        """
        parameter = 'partner_duplicate_mgmt.partner_name_similarity_{level}'.format(level=level)
        return self.env['ir.config_parameter'].sudo().get_param(parameter)

    def create_duplicates(self):
        res = self._find_duplicate_partner_ids()
        duplicates_sorted = [tuple(sorted(r)) for r in res]
        duplicates = list(set(duplicates_sorted))

        for dup in duplicates:
            self.create({'partner_1_id': dup[0], 'partner_2_id': dup[1]})

    def action_resolve(self):
        self.filtered(lambda x: x.state == 'to_validate').write({'state': 'resolved'})

        for record in self:
            message = _('The duplicate line ({partner_1}, {partner_2}) is resolved.').format(
                partner_1=record.partner_1_id.display_name,
                partner_2=record.partner_2_id.display_name,
            )
            record.partner_1_id.message_post(body=message)
            record.partner_2_id.message_post(body=message)

    def set_to_draft(self):
        self.write({'state': 'to_validate'})

    def open_partner_merge_wizard(self):
        if len(self) > 1:
            raise UserError(_("Please, select only one duplicate."))

        if self.state != 'to_validate':
            raise UserError(_("You can not merge a line which is not to validate."))

        merge_lines = self._create_merge_lines()
        self.write({'merge_line_ids': [(6, 0, merge_lines.ids)]})

        view = self.env.ref('partner_duplicate_mgmt.res_partner_merge_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'target': 'new',
            'res_id': self.id,
        }

    def _create_merge_lines(self):
        lines = self.env['res.partner.merge.line']
        duplicate_fields = self.env['res.partner.duplicate.field'].search([])
        partner_1 = self.partner_1_id
        partner_2 = self.partner_2_id

        for duplicate_field in duplicate_fields:
            field = partner_1._fields[duplicate_field.technical_name]
            partner_1_value = field.convert_to_display_name(
                getattr(partner_1, duplicate_field.technical_name),
                partner_1)
            partner_2_value = field.convert_to_display_name(
                getattr(partner_2, duplicate_field.technical_name),
                partner_2)

            lines |= self.env['res.partner.merge.line'].create({
                'duplicate_id': self.id,
                'duplicate_field_id': duplicate_field.id,
                'partner_1_value': partner_1_value,
                'partner_2_value': partner_2_value,
            })
        return lines


class ResPartnerDuplicateWithPartnerType(models.Model):
    """Add partner types on partner duplicates.

    Partner types are required to add define whether the merger reason
    is required for merging 2 partners.

    The merger reason is mandatory when both companies merged are companies.
    Merging companies is more critical then merging contacts.
    """

    _inherit = 'res.partner.duplicate'

    partner_1_type = fields.Selection(
        related='partner_1_id.company_type', string='Partner 1 Type')
    partner_2_type = fields.Selection(
        related='partner_2_id.company_type', string='Partner 2 Type')
