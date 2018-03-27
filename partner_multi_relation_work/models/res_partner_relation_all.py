# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ResPartnerRelationAll(models.AbstractModel):

    _inherit = 'res.partner.relation.all'

    is_work_relation = fields.Boolean(
        'Is Work Relation', related='type_selection_id.type_id.is_work_relation')

    @api.multi
    def write(self, vals):
        """Prevent updating work relations."""
        work_relations = self.filtered(lambda r: r.is_work_relation)
        if work_relations and not self.env.user.has_group('base.group_system'):
            raise AccessError(_(
                "You cannot update a partner relation that has been "
                "automatically created by the system. Only the system "
                "administrator can."
            ))
        return super(ResPartnerRelationAll, self).write(vals)

    @api.multi
    def unlink(self):
        """Prevent deleting work relations."""
        work_relations = self.filtered(lambda r: r.is_work_relation)
        if work_relations and not self.env.user.has_group('base.group_system'):
            raise AccessError(_(
                "You cannot delete a partner relation that has been "
                "automatically created by the system. Only the system "
                "administrator can."
            ))
        return super(ResPartnerRelationAll, self).unlink()

    @api.onchange('type_selection_id')
    def onchange_type_selection_id(self):
        res = super(ResPartnerRelationAll, self).onchange_type_selection_id()
        if self.type_selection_id.type_id.is_work_relation:
            res['warning'] = {
                'title': _('Warning'),
                'message': _(
                    'Work type relations cannot be created/updated manually. '
                    'If you need to add a new relation flagged as "Work '
                    'Relation", please use the "Change Parent Entity" button '
                    'on the partner form.'
                )
            }
            self.type_selection_id = False
        return res
