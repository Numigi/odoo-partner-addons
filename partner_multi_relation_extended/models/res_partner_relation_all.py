# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ResPartnerRelationAll(models.AbstractModel):

    _inherit = 'res.partner.relation.all'

    strength = fields.Many2one(
        string='Strength',
        comodel_name='res.partner.relation.strength',
    )

    note = fields.Char(
        'Note',
        help='Use this field to add information about the relation. For '
             'example, if the relation is "Belongs to the professional order",'
             ' you can put here the professional order number.',
    )

    is_automatic = fields.Char(
        'Automatic',
        readonly=True,
        help='This relation has been automatically created by the system. '
             'Only the system administrator can update or delete it.',
    )

    @api.model_cr_context
    def _auto_init(self):
        """
        Add new fields to auto_init
        """
        if 'strength' not in self._additional_view_fields:
            self._additional_view_fields.append('strength')
        if 'note' not in self._additional_view_fields:
            self._additional_view_fields.append('note')
        if 'is_automatic' not in self._additional_view_fields:
            self._additional_view_fields.append('is_automatic')
        return super(ResPartnerRelationAll, self)._auto_init()

    @api.multi
    def write(self, vals):
        """
        Only the administrator can update a partner relation which is
        automatic
        """
        user = self.env['res.users'].browse(self.env.uid)
        if not user.has_group('base.group_system') and any(
                self.mapped('is_automatic')):
            raise AccessError(_(
                "You cannot update a partner relation that has been "
                "automatically created by the system. Only the system "
                "administrator can."
            ))
        return super(ResPartnerRelationAll, self).write(vals)

    @api.multi
    def unlink(self):
        """
        Only the administrator can unlink a partner relation which is
        automatic
        """
        user = self.env['res.users'].browse(self.env.uid)
        if not user.has_group('base.group_system') and any(
                self.mapped('is_automatic')):
            raise AccessError(_(
                "You cannot delete a partner relation that has been "
                "automatically created by the system. Only the system "
                "administrator can."
            ))
        return super(ResPartnerRelationAll, self).unlink()
