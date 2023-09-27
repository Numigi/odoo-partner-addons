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

    is_company_parent = fields.Boolean(
        compute="_get_is_company_parent",
        store="True",
        string='Is a Parent Company',
        help="A parent company is a “Company” type contact for which at least "
             "one “Affiliate” is defined and for which no related"
             " company is defined"
    )

    @api.depends("company_type", "affiliate_ids", "parent_id")
    def _get_is_company_parent(self):
        _logger.info("compute if contact is a parent company or not %s" % self.ids)
        for rec in self:
            is_company_parent = False
            if rec.company_type == "company" and \
                    rec.affiliate_ids and not rec.parent_id:
                is_company_parent = True
            rec.is_company_parent = is_company_parent

    def compute_partner_parent_ids(self, rec=False, res=[]):
        _logger.info("compute_partner_parent_ids %s" % self.ids)
        if rec.parent_id:
            res.append(rec.parent_id.id)
            self.compute_partner_parent_ids(rec=rec.parent_id, res=res)
        return res

    @api.depends("parent_id", "child_ids")
    def _compute_highest_parent_id(self):
        _logger.info("_compute_highest_parent_id %s" % self.ids)
        for rec in self:
            if rec.parent_id:
                res = rec.compute_partner_parent_ids(rec=rec)
                if res:
                    rec.highest_parent_id = res[-1]
            else:
                rec.highest_parent_id = rec.id
            if rec.is_company_parent:
                rec.highest_parent_id = rec.id

    def compute_all_top_parent_id(self):
        _logger.info("compute_all_top_parent_id %s" % self.ids)
        # partner_ids = self.search([('is_company_parent', '=', False), ('parent_id', '!=', False)])
        # for partner in partner_ids:
        #     res = partner.compute_partner_parent_ids(rec=partner)
        #     if res:
        #         partner.highest_parent_id = res[-1]
        # parent_ids = self.search([('is_company_parent', '=', True), ('highest_parent_id', '=', False)])
        # for partner in parent_ids:
        #     partner.highest_parent_id = partner.id

    def update_all_child_ids(self, parent_id):
        _logger.info("update_all_child_ids %s" % self.ids)
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.id)])
        for rec in all_partners:
            if rec.is_company_parent:
                rec.highest_parent_id = self.id
            rec._compute_highest_parent_id()

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'parent_id' in vals:
            for record in self:
                self.update_all_child_ids(vals['parent_id'])
        return res







