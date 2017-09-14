# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class MergePartnerAutomatic(models.TransientModel):

    _inherit = 'base.partner.merge.automatic.wizard'

    def _get_fk_on(self, table):
        """
        Ignore the table 'res_partner_duplicate' to avoid merging partner
        duplicates.
        """
        res = super(MergePartnerAutomatic, self)._get_fk_on(table)
        relations = [r for r in res if 'res_partner_duplicate' not in r[0]]
        return relations

    @api.model
    def _update_reference_fields(self, src_partners, dst_partner):
        """
        Override completely the original function to avoid merging messages
        and merge only attachments.
        """
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_id = %(dst_partner)s
            WHERE res_model = 'res.partner'
            AND res_id = %(src_partner)s
        """, {
            'dst_partner': dst_partner.id,
            'src_partner': src_partners.id,
        })

    @api.model
    def _update_values(self, src_partners, dst_partner):
        """
        Avoid calling the original method which replaces partner preserved
        null values with the partner archived values.
        """
        return True
