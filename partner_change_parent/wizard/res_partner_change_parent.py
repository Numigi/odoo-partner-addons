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

    is_correction = fields.Boolean(
        "Correction Of The Parent Company",
        default=True,
        help="If checked, this action will directly modify the value of the "
        "field Parent Company on the existing contact. "
        "If not checked, the existing contact will be archived and a new "
        "contact will be created under the selected company."
    )

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

    def validate(self):
        """Reassign the contact to a new parent entity.

        In case of an internal user, the parent partner is changed directly.

        In case of a share partner, the current partner is archived.
        A copy of the partner is created with the new company.
        """
        self.ensure_one()

        if self.is_correction:
            return self._change_parent_directly()

        is_bound_to_user = self.contact_id.user_ids
        if is_bound_to_user:
            raise ValidationError(_(
                "The contact {contact} is bound to an active portal user. "
                "Before changing the parent entity, you must archive this user."
            ).format(contact=self.contact_id.display_name))

        else:
            return self._duplicate_contact_and_change_parent()

    def _archive_old_contact(self):
        """Archive the old contact."""
        self.contact_id.active = False

    def _change_parent_directly(self):
        """Change the parent entity without any other change to the contact."""
        self.contact_id.parent_id = self.new_company_id
        return True

    def _duplicate_contact_and_change_parent(self):
        """Duplicate the contact and change the parent.

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
        self.new_contact_id = self._copy_old_contact()
        self._archive_old_contact()
        return {
            'name': _('New Contact'),
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

        The address fields must be emptied.
        In Odoo version 11.0, the address of a contact can not be edited.
        It is automatically copied from the parent company. However, if the destination company
        does not have an address, the old address will not be removed. This is why we empty
        the address fields.

        The name of the contact must be rewritten after the copy to remove
        because Odoo automatically adds `(copy)`.

        :return: the new contact
        """
        # Remove the old email
        email = self.contact_id.email
        self.contact_id.email = ''

        # The parent partner is not propagated.
        default_values = {'parent_id': False}

        # The address fields must be emptied.
        address_fields = self.env['res.partner']._address_fields()
        default_values.update(((f, False) for f in address_fields))

        new_contact = self.contact_id.with_context(mail_notrack=True).copy(default=default_values)

        # Rename the new contact to remove `(copy)`.
        new_contact.with_context(mail_notrack=True).write({'name': self.contact_id.name})

        # Propagate the old email to the new contact.
        new_contact.with_context(mail_notrack=True).write({'email': email})

        # Set the new company on the new contact.
        new_contact.parent_id = self.new_company_id
        return new_contact


class ResPartnerParentChangeNoDuplicateCheck(models.TransientModel):
    """Binding between modules partner_change_parent and partner_duplicate_mgmt.

    When reassigning a contact to a new parent entity, the old contact is copied and
    archived. This binding prevents a partner duplicate line from being generated
    as a side effect of this process.
    """

    _inherit = 'res.partner.change.parent'

    def _copy_old_contact(self):
        return super(ResPartnerParentChangeNoDuplicateCheck,
                     self.with_context(disable_duplicate_check=True))._copy_old_contact()
