# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerRelationType(models.Model):

    _inherit = 'res.partner.relation.type'

    is_work_relation = fields.Boolean(
        'Work Relation',
    )

    is_same_relation = fields.Boolean(
        'Same Relation',
    )

    active = fields.Boolean(
        'Active', default=True,
    )

    @api.onchange('is_work_relation')
    def _onchange_is_work_relation(self):
        """
        A work relation is between an individual (left) and a company (right).
        """
        if self.is_work_relation:
            self.contact_type_left = 'p'
            self.contact_type_right = 'c'
            self.allow_self = False
            self.is_symmetric = False

    @api.constrains('is_work_relation')
    def _check_is_work_relation(self):
        """
        Make sure that only one relation type is categorized as work
        relation.
        A work relation is between an individual (left) and a company (right).
        """
        self.ensure_one()
        other_types = self.env['res.partner.relation.type'].search([]) - self
        if self.is_work_relation:
            if any(other_types.mapped('is_work_relation')):
                raise ValidationError(
                    _('There is already a Partner Relation Type categorized '
                      'as "Work Relation".')
                )
            else:
                self.contact_type_left = 'p'
                self.contact_type_right = 'c'
                self.allow_self = False
                self.is_symmetric = False

    @api.multi
    def unlink(self):
        """
        The relation type identified as 'same' cannot be deleted.
        """
        for relation_type in self:
            if relation_type.is_same_relation:
                raise ValidationError(_(
                    "You cannot delete the relation type which identifies two "
                    "partners as the same one. It is necessary in the parent "
                    "entity modification process."
                ))
        super(ResPartnerRelationType, self).unlink()
