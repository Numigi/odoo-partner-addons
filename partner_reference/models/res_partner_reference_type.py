# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerReferenceType(models.Model):

    _name = 'res.partner.reference.type'
    _description = 'Partner Reference Type'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
