# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerDateType(models.Model):

    _name = 'res.partner.date.type'
    _description = 'Contact Key Date Type'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
