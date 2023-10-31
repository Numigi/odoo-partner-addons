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
        _logger.info("2222")
        _logger.info(partner.name)
        return partner

    @api.depends("parent_id", "child_ids")
    def _compute_highest_parent_id(self):
        for rec in self:
            _logger.info("1111")
            _logger.info(rec.name)
            if rec.parent_id:
                rec.highest_parent_id = self._get_highest_parent(rec)
            elif not rec.parent_id and rec.company_type == "company":
                rec.highest_parent_id = rec.id
            else:
                rec.highest_parent_id = False

    @api.depends("company_type", "affiliate_ids", "parent_id")
    def _compute_is_company_parent(self):
        for rec in self:
            is_company_parent = False
            if rec.company_type == "company" and \
                    rec.affiliate_ids and not rec.parent_id:
                is_company_parent = True
            rec.is_company_parent = is_company_parent
