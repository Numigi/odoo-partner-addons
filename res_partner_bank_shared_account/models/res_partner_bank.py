# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ResPartnerBankSharedAccount(models.Model):

    _inherit = 'res.partner.bank'

    # TA#3966
    # voir https://www.odoo.com/fr_FR/forum/aide-1/question/remove-sql-constraints-5431
    _sql_constraints = [
        ('unique_number', 'Check(1=1)', 'Account Number must be unique'),
    ]
