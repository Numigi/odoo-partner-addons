# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import unidecode

_logger = logging.getLogger(__name__)


UPDATE_DUPLICATES_FIELDS = {
    'company_type',
    'firstname',
    'is_company',
    'lastname',
    'name',
    'parent_id',
}


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
        """Get the value for the field indexed_name.

        This field is used to search partners with a similar name.

        The following operations are done on the name to obtain the value to index:

        * Accents are removed.
        * All letters are lower case.

        :return: the value for the field indexed_name.
        """
        name_without_accents = unidecode.unidecode(self.name or '')
        return name_without_accents.lower()

    def _get_min_similarity(self, partner_name):
        """Get the minimum similiratity level required for a given partner name.

        A different similarity level is used depending on the length of the partner name.

        * level 1: 0 to 9 chars
        * level 2: 10 to 17 chars
        * level 3: 18 chars and more

        These values having tested with a significant sample of partner names.

        The reason for this complexity is that one letter of difference in a short
        partner name has a lot of impact on the similarity based on trigrams.

        :param partner_name: a partner name
        :return: the minimum similarity level in a scale from 0 to 1.
        """
        if not partner_name:
            partner_name = ''

        if len(partner_name) <= 9:
            return self.env['res.partner.duplicate']._get_partner_name_similarity(1)

        if 10 <= len(partner_name) <= 17:
            return self.env['res.partner.duplicate']._get_partner_name_similarity(2)

        if len(partner_name) >= 18:
            return self.env['res.partner.duplicate']._get_partner_name_similarity(3)

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

        return self.browse([r[0] for r in cr.fetchall()])

    @api.onchange('name', 'parent_id', 'company_type', 'is_company')
    def _onchange_name_find_duplicates(self):
        indexed_name = self._get_indexed_name()
        if self.id or not indexed_name:
            return

        duplicate_partners = self._get_duplicates(indexed_name)

        if duplicate_partners:
            duplicate_names = duplicate_partners.mapped('display_name')
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
        duplicates = self.env['res.partner']
        for partner in partners:
            self.env['res.partner.duplicate'].create({
                'partner_1_id': min(self.id, partner.id),
                'partner_2_id': max(self.id, partner.id),
            })
            duplicates |= self.browse(partner['id'])
        return duplicates

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

    def write(self, vals):
        updated_values = set(vals.keys())
        res = super(ResPartner, self).write(vals)

        if 'name' in vals:
            self._update_indexed_name()

        if any(f in updated_values for f in UPDATE_DUPLICATES_FIELDS):
            for record in self:
                duplicates = record._create_duplicates()
                record._post_message_duplicates(duplicates)

        return res

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
            'target': 'current',
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

    def action_merge(self):
        if not self.env.user.has_group('partner_duplicate_mgmt.group_duplicate_partners_control'):
            raise UserError(_("You don't have access to merge partners."))

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

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not self._context.get('duplicate_partner_1_id'):
            return super(ResPartner, self).name_search(
                name, args, operator, limit)

        partner_1 = self.browse(self._context.get('duplicate_partner_1_id'))
        partner_2 = self.browse(self._context.get('duplicate_partner_2_id'))
        return (partner_1 | partner_2).name_get()

    def _get_field_value(self, field_name):
        field_value = getattr(self, field_name)
        return self._fields[field_name].convert_to_write(field_value, self)
