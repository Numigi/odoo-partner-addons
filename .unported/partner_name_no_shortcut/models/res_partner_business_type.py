# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerBusinessType(models.Model):

    _name = 'res.partner.business.type'
    _description = 'Business Type'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)
