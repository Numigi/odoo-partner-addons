# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import AccessError


class ResPartnerRelationPreventModifySamePersonRelations(models.Model):
    """Prevent modifying a same-person relation by a non-admin user.

    Same person relations are used to identify 2 contacts that are
    the same person. These relations are automatically created when
    a contact changes from one entity to another.

    Same person relations can not be changed manually by a user.
    This is a design choice to prevent usage of this type of relation
    for any other use.
    """

    _inherit = 'res.partner.relation'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._prevent_modifying_same_person_relations()
        return res

    def write(self, vals):
        self._prevent_modifying_same_person_relations()
        super().write(vals)
        return True

    def unlink(self):
        self._prevent_modifying_same_person_relations()
        return super().unlink()

    def _prevent_modifying_same_person_relations(self):
        same_relations = self.filtered(lambda r: r.type_id.is_same_relation)
        if same_relations and not self.env.user.has_group('base.group_system'):
            raise AccessError(_(
                "Only the system administrator can create, delete or modify a "
                "same-person relation."))

    @api.onchange('type_selection_id')
    def onchange_type_selection_id(self):
        res = super().onchange_type_selection_id()
        if self.type_id.is_same_relation:
            res['warning'] = {
                'title': _('Warning'),
                'message': _('Same-person relations cannot be created/updated manually.')
            }
            self.type_selection_id = False
        return res
