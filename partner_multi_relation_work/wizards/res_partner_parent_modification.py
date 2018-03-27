# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerParentModification(models.TransientModel):

    _name = 'res.partner.parent.modification'
    _description = 'Partner Parent Modification'

    @api.model
    def _get_contact_id(self):
        return self.env.context.get('active_id')

    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        readonly=True,
        default=_get_contact_id,
    )

    new_company_id = fields.Many2one(
        comodel_name='res.partner',
        string='New Company',
        domain=[('is_company', '=', True)],
    )

    @api.multi
    def validate(self):
        """Reassign the contact to a new parent entity.

        * The old contact is copied.
        * The copy is placed under the destination entity.
        * Relations are created/updated between the involved partners.
        * The old contact is archived.

        This complex process for reassigning a contact to a new entity is
        required because otherwise, all objects previously related to the contact
        would follow the contact under the new entity.

        For example, we don't want invoices to follow the contact under the
        new entity. The commercial entity on an invoice must not be changed.
        """
        self.ensure_one()
        new_contact = self._copy_old_contact()

        self._copy_same_relations(new_contact)
        self._transfer_non_work_non_same_relations(new_contact)
        self._add_same_relation_with_old_contact(new_contact)
        self._add_new_work_relation(new_contact)

        self._archive_old_contact()

        return {
            'name': _('New Contact'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'res_id': new_contact.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
        }

    def _copy_old_contact(self):
        """Copy the old contact.

        The email must be removed from the old contact because of the unique
        constraint on res_partner.email.

        :return: the new contact
        """
        email = self.contact_id.email
        self.contact_id.email = ''
        new_contact = self.contact_id.copy(default={'parent_id': False})
        new_contact.write({
            'email': email,
            'parent_id': self.new_company_id,
        })
        return new_contact

    def _copy_same_relations(self, new_contact):
        """Copy old same-person relations to the new contact.

        Same-person relations are copied because a contact may change from one
        company to another multiple times.

        :param new_contact: the new generated contact.
        """
        relation_type_same = self.env.ref('partner_multi_relation_work.relation_type_same')
        same_person = self.env['res.partner.relation.all'].search([
            ('this_partner_id', '=', self.contact_id.id),
            ('type_selection_id.type_id', '=', relation_type_same.id),
        ])
        for old_identity in same_person:
            self.env['res.partner.relation'].create({
                'left_partner_id': new_contact.id,
                'type_id': relation_type_same.id,
                'right_partner_id': old_identity.other_partner_id.id,
            })

    def _transfer_non_work_non_same_relations(self, new_contact):
        """Transfer old relations that are not work or same-person relations to the new contact.

        :param new_contact: the new generated contact.
        """
        relation_type_same = self.env.ref('partner_multi_relation_work.relation_type_same')
        work_relation_type = self.env.ref('partner_multi_relation_work.relation_type_work')
        previous_relations = self.env['res.partner.relation.all'].\
            with_context(active_test=False).search([
                ('this_partner_id', '=', self.contact_id.id),
                ('type_selection_id.type_id', '!=', relation_type_same.id),
                ('type_selection_id.type_id', '!=', work_relation_type.id),
            ])
        for relation in previous_relations:
            relation.this_partner_id = new_contact.id

    def _add_same_relation_with_old_contact(self, new_contact):
        """Add a relation saying that the former contact and the new one are the same person.

        :param new_contact: the new generated contact.
        """
        relation_type_same = self.env.ref('partner_multi_relation_work.relation_type_same')
        self.env['res.partner.relation'].create({
            'left_partner_id': self.contact_id.id,
            'right_partner_id': new_contact.id,
            'type_id': relation_type_same.id,
            'is_automatic': True,
        })

    def _add_new_work_relation(self, new_contact):
        """Add a work relation between the new contact and the parent entity if required.

        :param new_contact: the new generated contact.
        """
        work_relation_type = self.env.ref('partner_multi_relation_work.relation_type_work')
        if self.new_company_id:
            self.env['res.partner.relation'].create({
                'left_partner_id': new_contact.id,
                'right_partner_id': self.new_company_id.id,
                'type_id': work_relation_type.id,
                'date_start': fields.Date.today(),
            })

    def _archive_old_contact(self):
        """Archive the old contact."""
        self.contact_id.active = False


class ResPartnerParentModificationNoDuplicateCheck(models.TransientModel):
    """Binding between modules partner_multi_relation_work and partner_duplicate_mgmt.

    When reassigning a contact to a new parent entity, the old contact is copied and
    archived. This binding prevents a partner duplicate line from being generated
    as a side effect of this process.
    """

    _inherit = 'res.partner.parent.modification'

    @api.multi
    def _copy_old_contact(self):
        return super(ResPartnerParentModificationNoDuplicateCheck,
                     self.with_context(disable_duplicate_check=True))._copy_old_contact()
