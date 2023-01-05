# -*- coding: utf-8 -*-
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class MergePartnerAutomaticPreventPropagateRelations(models.TransientModel):
    """Prevent base.partner.merge from propagating relations."""

    _inherit = 'base.partner.merge.automatic.wizard'

    def _get_fk_on(self, table):
        """Remove partner relations from the list of table to update.

        The method _get_fk_on is used to define which foreign keys must be redirected
        from the archived partner to the preserved partner.

        We remove partner relations so that relations are managed by the
        method merge_partners of res.partner.duplicate.
        """
        foreign_keys = super()._get_fk_on(table)
        return [r for r in foreign_keys if 'res_partner_relation' not in r[0]]
