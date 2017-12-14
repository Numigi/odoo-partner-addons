# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models, SUPERUSER_ID
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger('base.partner.merge')


class MergePartnerAutomatic(models.TransientModel):

    _inherit = 'base.partner.merge.automatic.wizard'

    def _get_fk_on(self, table):
        """
        Ignore the table 'res_partner_duplicate' to avoid merging partner
        duplicates.
        """
        if ('merge_2_companies' in self.env.context):
            return []

        res = super(MergePartnerAutomatic, self)._get_fk_on(table)
        relations = [r for r in res if 'res_partner_duplicate' not in r[0]]
        return relations

    @api.model
    def _update_reference_fields(self, src_partners, dst_partner):
        """
        Override completely the original function to avoid merging messages
        and merge only attachments.
        """
        if src_partners.is_company and dst_partner.is_company:
            return

        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_id = %(dst_partner)s
            WHERE res_model = 'res.partner'
            AND res_id = %(src_partner)s
        """, {
            'dst_partner': dst_partner.id,
            'src_partner': src_partners.id,
        })

    def _update_children(self, src_partners, dst_partner):
        src_partners.child_ids.write({'parent_id': dst_partner.id})
        src_partners.write({
            'is_company': False,
            'parent_id': dst_partner.id,
        })

    def _merge(self, partner_ids, dst_partner):
        """
        Override completely the original function to remove useless code.
        """
        Partner = self.env['res.partner']
        partner_ids = Partner.browse(partner_ids).exists()

        # check only admin can merge partners with different emails
        if (
            SUPERUSER_ID != self.env.uid and
            len(set(partner.email for partner in partner_ids)) > 1
        ):
            raise UserError(_(
                "All contacts must have the same email. Only the "
                "Administrator can merge contacts with different emails."))

        # remove dst_partner from partners to merge
        if dst_partner and dst_partner in partner_ids:
            src_partners = partner_ids - dst_partner
        else:
            ordered_partners = self._get_ordered_partner(partner_ids.ids)
            dst_partner = ordered_partners[-1]
            src_partners = ordered_partners[:-1]
        _logger.info("dst_partner: %s", dst_partner.id)

        # FIXME: is it still required to make and exception for
        # account.move.line since accounting v9.0 ?
        if (
            SUPERUSER_ID != self.env.uid and
            'account.move.line' in self.env and
            self.env['account.move.line'].sudo().search([
                ('partner_id', 'in', [partner.id for partner in src_partners])
            ])
        ):
            raise UserError(_(
                "Only the destination contact may be linked to existing "
                "Journal Items. Please ask the Administrator if you need "
                "to merge several contacts linked to existing Journal Items."))

        self._update_reference_fields(src_partners, dst_partner)

        # call sub methods to do the merge
        if src_partners.is_company and dst_partner.is_company:
            self.with_context({'merge_2_companies': True})\
                ._update_foreign_keys(src_partners, dst_partner)
            self._update_children(src_partners, dst_partner)
        else:
            self._update_foreign_keys(src_partners, dst_partner)

        _logger.info(
            '(uid = %s) merged the partners %r with %s',
            self._uid, src_partners.ids, dst_partner.id)
