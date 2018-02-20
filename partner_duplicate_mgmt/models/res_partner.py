# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import unidecode

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    indexed_name = fields.Char('Indexed Name')

    duplicate_ids = fields.Many2many(
        'res.partner', relation='rel_partner_duplicate',
        column1='partner_id', column2='duplicate_id',
        compute='_compute_duplicate_ids', string='Duplicate Partners')

    duplicate_1_ids = fields.One2many(
        'res.partner.duplicate', inverse_name='partner_2_id',
        domain=[('state', '=', 'to_validate')])
    duplicate_2_ids = fields.One2many(
        'res.partner.duplicate', inverse_name='partner_1_id',
        domain=[('state', '=', 'to_validate')])
    duplicate_count = fields.Integer(compute='_compute_duplicate_ids')

    company_type = fields.Selection(store=True)

    @api.depends('duplicate_1_ids', 'duplicate_2_ids')
    def _compute_duplicate_ids(self):
        for rec in self:
            dups_1 = rec.mapped('duplicate_1_ids.partner_1_id')
            dups_2 = rec.mapped('duplicate_2_ids.partner_2_id')
            rec.duplicate_ids = (dups_1 | dups_2)
            rec.duplicate_count = len(rec.duplicate_ids)

    def _get_indexed_name(self):
        if not self.name:
            return ''

        indexed_name = self.name
        terms = self.env['res.partner.duplicate.term'].search([])
        spaces_begining = '(^|\s+)'
        spaces_end = '($|\s+)'

        for term in terms:
            expression = term.expression
            if term.type != 'regex':
                expression = (
                    spaces_begining + re.escape(expression) + spaces_end)

            indexed_name = re.sub(
                expression, ' ', indexed_name, flags=re.IGNORECASE)

        indexed_name = unidecode.unidecode(indexed_name)
        return indexed_name.strip().lower()

    def _get_min_similarity(self, indexed_name):
        if len(indexed_name) <= 9:
            return self.env['ir.config_parameter'].get_param(
                'partner_duplicate_mgmt.partner_name_similarity_1')

        if 10 <= len(indexed_name) <= 17:
            return self.env['ir.config_parameter'].get_param(
                'partner_duplicate_mgmt.partner_name_similarity_2')

        if len(indexed_name) >= 18:
            return self.env['ir.config_parameter'].get_param(
                'partner_duplicate_mgmt.partner_name_similarity_3')

    def _get_duplicates(self, indexed_name=None):
        if self._context.get('disable_duplicate_check'):
            return []

        if not indexed_name:
            indexed_name = self.indexed_name

        min_similarity = self._get_min_similarity(indexed_name)

        cr = self.env.cr
        cr.execute('SELECT set_limit(%s)', (min_similarity,))
        cr.execute("""
            SELECT p.id
            FROM res_partner p
            WHERE p.id != %(id)s
            AND p.active = true
            AND p.indexed_name %% %(name)s
            AND p.company_type = %(company_type)s
            AND ((p.parent_id IS NOT DISTINCT FROM %(parent)s)
              OR (p.parent_id IS NULL AND p.id != %(parent)s)
              OR (%(parent)s IS NULL AND %(id)s != p.parent_id))
            AND NOT EXISTS (
                SELECT NULL
                FROM res_partner_duplicate d
                WHERE (d.partner_1_id = p.id AND d.partner_2_id = %(id)s)
                OR    (d.partner_1_id = %(id)s AND d.partner_2_id = p.id)
            )
        """, {
            'id': self.id or self._origin.id or 0,
            'company_type': self.company_type,
            'name': indexed_name or '',
            'parent': self.parent_id.id or None,
        })

        res = cr.fetchall()
        ids = [p[0] for p in res]
        return self.browse(ids)

    @api.onchange('name', 'parent_id', 'company_type', 'is_company')
    def onchange_name(self):
        indexed_name = self._get_indexed_name()
        if self.id or not indexed_name:
            return

        duplicate_dict = self._get_duplicates(indexed_name)

        if duplicate_dict:
            duplicate_names = [d['name'] for d in duplicate_dict]
            partner_names = ", ".join(duplicate_names)
            return {
                'warning': {
                    'title': 'Warning',
                    'message': _(
                        "This partner (%(new_partner)s) may be considered "
                        "as a duplicate of the following partner(s): "
                        "%(partner_names)s.") % {
                            'new_partner': self.name,
                            'partner_names': partner_names,
                    }}}

    def _update_indexed_name(self):
        for partner in self:
            indexed_name = partner._get_indexed_name()
            partner.write({'indexed_name': indexed_name})

    def _create_duplicates(self):
        partners = self._get_duplicates()
        duplicates = self.env['res.partner.duplicate']
        for partner in partners:
            duplicated_partners = (partner | self).sorted('id')
            duplicates |= self.env['res.partner.duplicate'].create({
                'partner_1_id': duplicated_partners[0].id,
                'partner_2_id': duplicated_partners[1].id,
            })

        return partners

    def _post_message_duplicates(self, duplicates):
        for record in self:
            if duplicates:
                partner_names = ', '.join(duplicates.mapped('name'))
                message = _('Duplicate Partners : %s') % (partner_names)
                record.message_post(body=message)

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        res._update_indexed_name()
        duplicates = res._create_duplicates()
        res._post_message_duplicates(duplicates)

        return res

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        # if 'name' in vals or 'firstname' in vals or 'lastname' in vals:
            # self._update_indexed_name()

        if (
            'parent_id' in vals or 'name' in vals or
            'lastname' in vals or 'firstname' in vals or
            'company_type' in vals or 'is_company' in vals
        ):
            self._update_indexed_name()

            for record in self:
                duplicates = record._create_duplicates()
                record._post_message_duplicates(duplicates)

        return res

    @api.multi
    def action_view_duplicates(self):
        self.ensure_one()
        action = self.env.ref('contacts.action_contacts')
        partners = self.duplicate_ids

        res = {
            'name': action.name,
            'type': action.type,
            'res_model': action.res_model,
            'view_type': action.view_type,
            'view_mode': 'tree,form',
            'views': [(action.view_id.id, 'tree'), (False, 'form')],
            'search_view_id': action.search_view_id.id,
            'context': action.context,
            'target': 'new',
            'domain': [
                ('id', 'in', partners.ids),
            ],
        }

        if len(partners) == 1:
            res['view_id'] = (
                self.env.ref('partner_duplicate_mgmt.view_partner_form').id)
            res['view_mode'] = 'form'
            res['res_id'] = partners.id
            del res['views']

        return res

    @api.model_cr_context
    def _auto_init(self):
        res = super(ResPartner, self)._auto_init()
        cr = self._cr

        cr.execute("""
            SELECT name, installed
            FROM pg_available_extension_versions
            WHERE name='pg_trgm' AND installed=true
            """)
        if not cr.fetchone():
            try:
                cr.execute('CREATE EXTENSION pg_trgm')
            except:
                message = (
                    "Could not create the pg_trgm postgresql EXTENSION. "
                    "You must log to your database as superuser and type "
                    "the following command:\nCREATE EXTENSION pg_trgm."
                )
                _logger.warning(message)
                raise Exception(message)

        cr.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE indexname='res_partner_indexed_name_gin'
            """)
        if not cr.fetchone():
            cr.execute("""
                CREATE INDEX res_partner_indexed_name_gin
                ON res_partner USING gin(indexed_name gin_trgm_ops)
                """)
        return res

    @api.multi
    def action_merge(self):
        group = self.env.ref(
            'partner_duplicate_mgmt.group_duplicate_partners_control')
        if group not in self.env.user.groups_id:
            raise UserError(_(
                "You don't have access to merge partners."))

        if len(self) != 2:
            raise UserError(_("Please, select two partners to merge."))

        if self[0].company_type != self[1].company_type:
            raise UserError(_("You can not merge a company with a contact."))

        duplicate = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', self.ids),
            ('partner_2_id', 'in', self.ids),
        ], limit=1)

        if not duplicate:
            duplicate = self.env['res.partner.duplicate'].create(
                {'partner_1_id': self[0].id, 'partner_2_id': self[1].id})

        if duplicate.state != 'to_validate':
            view = self.env.ref(
                'partner_duplicate_mgmt.res_partner_duplicate_form')
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner.duplicate',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view.id, 'form')],
                'res_id': duplicate.id,
            }

        return duplicate.open_partner_merge_wizard()

    @api.model
    def hide_merge_selected_contacts_action(self):
        action = self.env['ir.actions.act_window'].search([
            ('name', '=', 'Merge Selected Contacts')])
        if action:
            action.unlink()

    @api.multi
    def name_get(self):
        if self.env.context.get('order_by_id'):
            return super(ResPartner, self.sorted('id')).name_get()

        if self.env.context.get('show_address'):
            res = []
            for partner in self:
                res.append((
                    partner.id,
                    '%s (%s)' % (partner.display_name, partner.street or '',)))

            return res

        return super(ResPartner, self).name_get()
