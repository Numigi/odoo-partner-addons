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
            if rec.company_type == "company" and \
                    rec.affiliate_ids and not rec.parent_id:
                rec.is_company_parent = True
            else:
                rec.is_company_parent = False

    @api.depends("parent_id", "child_ids")
    def _get_highest_parent_id(self):
        for rec in self:
            if rec.parent_id:
                res = rec.get_parent_id_level_zero(rec=rec)
                if res:
                    rec.highest_parent_id = res[-1]

    def get_parent_id_level_zero(self, rec=False, res=[]):
        if rec.parent_id:
            res.append(rec.parent_id.id)
            self.get_parent_id_level_zero(rec=rec.parent_id, res=res)
        return res

    def cron_compute_highest_parent_id(self):
        partner_ids = self.search([('is_company_parent', '=', False),
                                   ('parent_id', '!=', False)])
        for partner in partner_ids:
            res = partner.get_parent_id_level_zero(rec=partner)
            partner.highest_parent_id = res[-1]



