# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    highest_parent_id = fields.Many2one(
        "res.partner",
        compute="_get_highest_parent_id",
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
        """compute if contact is a parent company or not"""
        for rec in self:
            is_company_parent = False
            if rec.company_type == "company" and \
                    rec.affiliate_ids and not rec.parent_id:
                is_company_parent = True
            rec.is_company_parent = is_company_parent

    def find_top_parent(self, partner):
        self.ensure_one()
        if not partner.parent_id:
            return partner.id
        else:
            parent = partner.parent_id
            return self.find_top_parent(parent)

    @api.depends("parent_id", "child_ids")
    def _get_highest_parent_id(self):
        for rec in self:
            if rec.parent_id:
                rec.highest_parent_id = rec.find_top_parent(rec)
            else:
                rec.highest_parent_id = False
