# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    highest_parent_id = fields.Many2one(
        "res.partner",
        compute="_compute_highest_parent_id",
        store="True",
        string="Highest parent"
    )

    all_child_ids = fields.One2many(
        string='All Children of the highest parent company',
        comodel_name='res.partner',
        inverse_name='highest_parent_id',
    )

    is_company_parent = fields.Boolean(
        compute="_compute_is_company_parent",
        store="True",
        string='Is a Parent Company',
        help="A parent company is a “Company” type contact for which at least "
             "one “Affiliate” is defined and for which no related"
             " company is defined"
    )

    def _get_highest_parent(self, partner):
        while partner.parent_id:
            partner = partner.parent_id
        return partner

    @api.depends("company_type", "affiliate_ids", "parent_id", "child_ids", )
    def _compute_highest_parent_id(self):
        for rec in self:
            if rec.parent_id:
                rec.highest_parent_id = self._get_highest_parent(rec)
            elif not rec.parent_id and rec.company_type == "company":
                rec.highest_parent_id = rec.id
            else:
                rec.highest_parent_id = False

    @api.depends("company_type", "affiliate_ids", "parent_id", "child_ids")
    def _compute_is_company_parent(self):
        for rec in self:
            is_company_parent = False
            if rec.company_type == "company" and \
                    rec.affiliate_ids and not rec.parent_id:
                is_company_parent = True
            rec.is_company_parent = is_company_parent

    def compute_affiliates_highest_parent_id(self, affiliates):
        affiliates._compute_highest_parent_id()
        for sub_affiliate in affiliates.affiliate_ids:
            self.compute_affiliates_highest_parent_id(sub_affiliate)

    def compute_childs_highest_parent_id(self, childs):
        childs._compute_highest_parent_id()
        for sub_childs in childs.affiliate_ids:
            self.compute_affiliates_highest_parent_id(sub_childs)

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'parent_id' in vals:
            for record in self:
                self.compute_affiliates_highest_parent_id(record.affiliate_ids)
                self.compute_childs_highest_parent_id(record.child_ids)
        return res
