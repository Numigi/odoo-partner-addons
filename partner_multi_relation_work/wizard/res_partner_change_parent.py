# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerParentChangeWithRelations(models.TransientModel):
    """When changing the entity of a contact, update/add partner relations."""

    _inherit = 'res.partner.change.parent'

    def _duplicate_contact_and_change_parent(self):
        """Add/update relations on between partners."""
        res = super()._duplicate_contact_and_change_parent()
        self._copy_same_relations()
        self._transfer_non_work_non_same_relations()
        self._add_same_relation_with_old_contact()

        if self.contact_id.parent_id:
            self._terminate_old_work_relations()

        if self.new_company_id:
            self._add_new_work_relation()

        self._transfer_work_relations()
        return res

    def _copy_same_relations(self):
        """Copy old same-person relations to the new contact.

        Same-person relations are copied because a contact may change from one
        company to another multiple times.
        """
        relation_type_same = self._get_same_relation_type()
        same_person = self.env['res.partner.relation.all'].search([
            ('this_partner_id', '=', self.contact_id.id),
            ('type_selection_id.type_id', '=', relation_type_same.id),
        ])
        for old_identity in same_person:
            # Same partner relations can not be created manually by a user.
            # This is why .sudo() is required.
            self.env['res.partner.relation'].sudo().create({
                'left_partner_id': self.new_contact_id.id,
                'type_id': relation_type_same.id,
                'right_partner_id': old_identity.other_partner_id.id,
            })

    def _transfer_non_work_non_same_relations(self):
        """Transfer old relations that are not work or same-person
        relations to the new contact."""
        relation_type_same = self._get_same_relation_type()
        work_relation_type = self._get_work_relation_type()
        previous_relations = self.env['res.partner.relation.all'].\
            with_context(active_test=False).search([
                ('this_partner_id', '=', self.contact_id.id),
                ('type_selection_id.type_id', '!=', relation_type_same.id),
                ('type_selection_id.type_id', '!=', work_relation_type.id),
            ])
        for relation in previous_relations:
            relation.this_partner_id = self.new_contact_id.id

    def _transfer_work_relations(self):
        """Transfer old work relations to the new contact."""
        work_relation_type = self._get_work_relation_type()
        previous_relations = self.env['res.partner.relation.all'].\
            with_context(active_test=False).search([
                ('this_partner_id', '=', self.contact_id.id),
                ('type_selection_id.type_id', '=', work_relation_type.id),
            ])
        for relation in previous_relations:
            relation.this_partner_id = self.new_contact_id.id

    def _add_same_relation_with_old_contact(self):
        """Add a relation saying that the former contact and the new one are the same person."""
        relation_type_same = self._get_same_relation_type()

        # Same partner relations can not be created manually by a user.
        # This is why .sudo() is required.
        self.env['res.partner.relation'].sudo().create({
            'left_partner_id': self.contact_id.id,
            'right_partner_id': self.new_contact_id.id,
            'type_id': relation_type_same.id,
        })

    def _terminate_old_work_relations(self):
        """Add an end date to the work relations with the previous company."""
        work_relation_type = self._get_work_relation_type()
        previous_relations = self.env['res.partner.relation.all'].\
            with_context(active_test=False).search([
                ('this_partner_id', '=', self.contact_id.id),
                ('other_partner_id', '=', self.contact_id.parent_id.id),
                ('type_selection_id.type_id', '=', work_relation_type.id),
                ('date_end', '=', False),
            ])
        for relation in previous_relations:
            relation.date_end = fields.Date.context_today(self)

    def _add_new_work_relation(self):
        """Add a work relation between the new contact and the parent entity."""
        work_relation_type = self._get_work_relation_type()
        self.env['res.partner.relation'].create({
            'left_partner_id': self.new_contact_id.id,
            'right_partner_id': self.new_company_id.id,
            'type_id': work_relation_type.id,
            'date_start': fields.Date.context_today(self),
        })

    def _get_same_relation_type(self):
        return self.env.ref('partner_multi_relation_work.relation_type_same')

    def _get_work_relation_type(self):
        return self.env.ref('partner_multi_relation_work.relation_type_work')
