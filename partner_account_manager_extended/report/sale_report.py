# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    account_manager_id = fields.Many2one(
        "res.users",
        "Responsible",
        readonly=True
    )

    def _group_by_sale(self, groupby=''):
        res = super()._group_by_sale(groupby)
        res += """,s.account_manager_id"""
        return res

    def _select_additional_fields(self, fields):
        fields['account_manager_id'] =\
            ", s.account_manager_id as account_manager_id"
        return super()._select_additional_fields(fields)
