# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    qst = fields.Char(string="QST")
    country_code = fields.Char(related="country_id.code", store=True)
