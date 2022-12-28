# -*- coding: utf-8 -*-
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ResPartnerDuplicateWithRelationPropagation(models.Model):
    """Propagate relations from the preserved partner to the archived partner."""

    _inherit = 'res.partner.duplicate'

    def merge_partners(self):
        res = super().merge_partners()
        self._process_relations()
        return res

    def _process_relations(self):
        """Process relations for which the left partner is partner to archive.

        If a similar relation exists on the preserved partner, then it is deleted.
        Otherwise, the relation is updated to point on the preserved partner.

        2 equivalent relations are relations that have the same partners and
        the same type.
        """
        self._process_left_relations()
        self._process_right_relations()

    def _process_left_relations(self):
        """Process relations for which the left partner is partner to archive."""
        relation_cls = self.env['res.partner.relation'].with_context(active_test=False)

        relations_left = relation_cls.search([
            ('left_partner_id', '=', self.partner_archived_id.id),
            ('right_partner_id', '!=', self.partner_preserved_id.id),
        ])

        for relation in relations_left:
            equivalent_relation = relation_cls.search([
                ('left_partner_id', '=', self.partner_preserved_id.id),
                ('type_id', '=', relation.type_id.id),
            ])

            if equivalent_relation:
                relation.unlink()
            else:
                relation.left_partner_id = self.partner_preserved_id.id

    def _process_right_relations(self):
        """Process relations for which the right partner is partner to archive."""
        relation_cls = self.env['res.partner.relation'].with_context(active_test=False)

        relations_right = relation_cls.search([
            ('right_partner_id', '=', self.partner_archived_id.id),
            ('left_partner_id', '!=', self.partner_preserved_id.id),
        ])

        for relation in relations_right:
            equivalent_relation = relation_cls.search([
                ('right_partner_id', '=', self.partner_preserved_id.id),
                ('type_id', '=', relation.type_id.id),
            ])

            if equivalent_relation:
                relation.unlink()
            else:
                relation.right_partner_id = self.partner_preserved_id.id
