# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerRelationTypeSameRelation(models.Model):

    _inherit = 'res.partner.relation.type'

    is_same_relation = fields.Boolean('Same Relation', compute='_compute_is_same_relation')

    def _compute_is_same_relation(self):
        is_same_relation = self.env.ref('partner_multi_relation_work.relation_type_same')
        for rec in self:
            rec.is_same_relation = rec == is_same_relation

    @api.constrains('contact_type_left', 'contact_type_right')
    def _check_same_relation_from_individual_to_individual(self):
        """Check that same-person relations are between two individuals."""
        same_relations = self.filtered(lambda t: t.is_same_relation)
        for rec in same_relations:
            if rec.contact_type_left != 'p' or rec.contact_type_right != 'p':
                raise ValidationError(
                    _('Same-person relations must be between an individual (left) '
                      'and an individual (right).'))

    @api.constrains('is_symmetric')
    def _check_work_relation_is_not_symmetric(self):
        """Check that same-person relations are symetric."""
        symetric_same_relations = self.filtered(lambda t: t.is_same_relation and t.is_symmetric)
        if symetric_same_relations:
            raise ValidationError(_('Same-person relations must be symmetric.'))

    @api.constrains('allow_self')
    def _check_work_relation_does_not_allow_self(self):
        """Check that same-person relations are not allowed between a partner and himself."""
        same_relations_with_self = self.filtered(lambda t: t.is_same_relation and t.allow_self)
        if same_relations_with_self:
            raise ValidationError(
                _('Same-person relations are not possible between a partner and the same partner. '
                  'This type of relation is reserved for 2 distincs partner rows in the database.'))


class ResPartnerRelationTypeWorkRelation(models.Model):

    _inherit = 'res.partner.relation.type'

    is_work_relation = fields.Boolean('Work Relation', compute='_compute_is_work_relation')

    def _compute_is_work_relation(self):
        is_work_relation = self.env.ref('partner_multi_relation_work.relation_type_work')
        for rec in self:
            rec.is_work_relation = rec == is_work_relation

    @api.constrains('contact_type_left', 'contact_type_right')
    def _check_work_relation_from_individual_to_company(self):
        """Check that work relations are between an individual (left) and a company (right)."""
        work_relations = self.filtered(lambda t: t.is_work_relation)
        for rec in work_relations:
            if rec.contact_type_left != 'p' or rec.contact_type_right != 'c':
                raise ValidationError(
                    _('Work relations must be between an individual (left) and a company (right).'))

    @api.constrains('is_symmetric')
    def _check_work_relation_is_not_symmetric(self):
        """Check that work relations are symetric."""
        symetric_work_relations = self.filtered(lambda t: t.is_work_relation and t.is_symmetric)
        if symetric_work_relations:
            raise ValidationError(_('Work relations must be symmetric.'))

    @api.constrains('allow_self')
    def _check_work_relation_does_not_allow_self(self):
        """Check that work relations are not allowed between a partner and himself."""
        work_relations_with_self = self.filtered(lambda t: t.is_work_relation and t.allow_self)
        if work_relations_with_self:
            raise ValidationError(
                _('Work relations are not possible between a partner and himself.'))
