# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
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
        """
        At validation, the wizard duplicates the old contact. The new contact
        gets its new parent, and the wizard creates a new automatic
        relation saying that both contacts are the same person. The wizard
        also closes all former relations and archives the old contact.
        """
        self.ensure_one()
        relation_type_same = self.env.ref(
                'partner_multi_relation_extended.rel_type_same')

        # Search for the work relation type
        work_relation_type = self.env['res.partner.relation.type'].search([
            ('is_work_relation', '=', True),
        ])
        if not work_relation_type:
            raise ValidationError(_(
                'Prior to attribute a new work relation, you need to define a '
                'partner relation type flagged as "Work Relation".'
            ))

        # Duplicate the contact. Remove the email of the former contact.
        # Remove the (copy) addendum in the name of the new contact.
        # Change parent for the new contact.
        email = self.contact_id.email
        self.contact_id.email = ''
        ctx = self.env.context.copy()
        ctx.update({'disable_duplicate_check': True})
        new_contact = self.contact_id.with_context(ctx).copy(
            default={'parent_id': False})
        new_contact.name = new_contact.name[:-7]
        new_contact.email = email
        new_contact.parent_id = self.new_company_id

        # Keep all the relations saying that the contacts are the same person
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

        # Add a relation saying that the former contact and the new one are
        # the same person.
        self.env['res.partner.relation'].create({
            'left_partner_id': self.contact_id.id,
            'right_partner_id': new_contact.id,
            'type_id': relation_type_same.id,
            'is_automatic': True,
        })

        # Add the new work relation
        if self.new_company_id:
            self.env['res.partner.relation'].create({
                'left_partner_id': new_contact.id,
                'right_partner_id': self.new_company_id.id,
                'type_id': work_relation_type.id,
                'date_start': fields.Date.today(),
            })

        # Transfer all previous relations from the former contact
        previous_relations = self.env['res.partner.relation.all'].search([
            ('this_partner_id', '=', self.contact_id.id),
            ('is_automatic', '=', False),
            ('type_selection_id.type_id', '!=', relation_type_same.id),
            ('type_selection_id.type_id.is_work_relation', '=', False),
            '|', ('active', '=', False), ('active', '=', True)
        ])
        for relation in previous_relations:
            relation.this_partner_id = new_contact.id
            relation.onchange_partner_id()

        # Archive the former contact
        self.contact_id.active = False

        # Return the new contact form
        return {
            'name': _('New Contact'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'res_id': new_contact.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
        }
