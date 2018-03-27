# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerParentChange(models.TransientModel):

    _name = 'res.partner.change.parent'
    _description = 'Partner Parent Change Wizard'

    @api.model
    def _get_contact_id(self):
        return self.env.context.get('active_id')

    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        readonly=True,
        default=_get_contact_id,
    )

    new_contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        readonly=True,
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
        self.new_contact_id = self._copy_old_contact()
        self._archive_old_contact()
        return {
            'name': _('New Contact'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'res_id': self.new_contact_id.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
        }

    def _copy_old_contact(self):
        """Copy the old contact.

        The email must be removed from the old contact because of the unique
        constraint on res_partner.email.

        The name of the contact must be rewritten after the copy to remove
        because Odoo automatically adds `(copy)`.

        :return: the new contact
        """
        email = self.contact_id.email
        self.contact_id.email = ''
        new_contact = self.contact_id\
            .with_context(mail_notrack=True)\
            .copy(default={'parent_id': False})

        new_contact.with_context(mail_notrack=True).write({
            'name': self.contact_id.name,
            'email': email,
        })

        new_contact.parent_id = self.new_company_id
        return new_contact

    def _archive_old_contact(self):
        """Archive the old contact."""
        self.contact_id.active = False


class ResPartnerParentChangeNoDuplicateCheck(models.TransientModel):
    """Binding between modules partner_change_parent and partner_duplicate_mgmt.

    When reassigning a contact to a new parent entity, the old contact is copied and
    archived. This binding prevents a partner duplicate line from being generated
    as a side effect of this process.
    """

    _inherit = 'res.partner.change.parent'

    @api.multi
    def _copy_old_contact(self):
        return super(ResPartnerParentChangeNoDuplicateCheck,
                     self.with_context(disable_duplicate_check=True))._copy_old_contact()
