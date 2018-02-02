# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerDuplicateTerm(models.Model):

    _name = 'res.partner.duplicate.term'
    _description = 'Partner Duplicate Term'

    type = fields.Selection(
        string='Type',
        required=True,
        selection=[
            ('string', 'String'),
            ('regex', 'Regular Expression')
        ], default='string',
    )

    expression = fields.Char(string='Expression', required=True)

    active = fields.Boolean('Active', default=True)
