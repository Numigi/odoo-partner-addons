# © 2017-201 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MergerReason(models.Model):

    _name = 'merger.reason'
    _description = 'Merger Reason'

    name = fields.Char('Name', required=True, translate=True)
