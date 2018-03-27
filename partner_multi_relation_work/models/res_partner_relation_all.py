# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ResPartnerRelationPreventModifyWorkRelations(models.Model):
    """Prevent modifying a work relation by a non-admin user."""

    _inherit = 'res.partner.relation'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._prevent_modifying_work_relations()
        return res

    @api.multi
    def write(self, vals):
        self._prevent_modifying_work_relations()
        super().write(vals)
        self._prevent_modifying_work_relations()
        return True

    @api.multi
    def unlink(self):
        self._prevent_modifying_work_relations()
        return super().unlink()

    def _prevent_modifying_work_relations(self):
        work_relations = self.filtered(lambda r: r.type_id.is_work_relation)
        if work_relations and not self.env.user.has_group('base.group_system'):
            raise AccessError(_(
                "Only the system administrator can create, delete or modify a work relation."))

    @api.onchange('type_selection_id')
    def onchange_type_selection_id(self):
        res = super().onchange_type_selection_id()
        if self.type_id.is_work_relation:
            res['warning'] = {
                'title': _('Warning'),
                'message': _(
                    'Work relations cannot be created/updated manually. '
                    'If you need to add a new relation flagged as "Work '
                    'Relation", please use the "Change Parent Entity" button '
                    'on the partner form.'
                )
            }
            self.type_selection_id = False
        return res


class ResPartnerRelationPreventModifySamePersonRelations(models.Model):
    """Prevent modifying a same-person relation by a non-admin user."""

    _inherit = 'res.partner.relation'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._prevent_modifying_same_person_relations()
        return res

    @api.multi
    def write(self, vals):
        self._prevent_modifying_same_person_relations()
        super().write(vals)
        self._prevent_modifying_same_person_relations()
        return True

    @api.multi
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
                'message': _(
                    'Same-person relations cannot be created/updated manually. '
                    'If you need to add a new relation flagged as "Work '
                    'Relation", please use the "Change Parent Entity" button '
                    'on the partner form.'
                )
            }
            self.type_selection_id = False
        return res
