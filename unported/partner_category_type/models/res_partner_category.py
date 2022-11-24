# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerCategory(models.Model):

    _inherit = 'res.partner.category'

    type = fields.Selection([
        ('organization_type', 'Organization Type'),
        ('profile', 'Profile'),
        ('personality', 'Personality'),
        ('job_position', 'Job Position')
    ], string='Type')
