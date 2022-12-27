# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    reference_ids = fields.One2many(
        'res.partner.reference', 'partner_id', copy=False)
