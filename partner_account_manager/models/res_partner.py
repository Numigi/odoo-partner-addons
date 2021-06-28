# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class Partner(models.Model):

    _inherit = "res.partner"

    account_manager_id = fields.Many2one("res.users")
