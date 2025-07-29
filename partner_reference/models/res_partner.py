# -*- coding: utf-8 -*-
# © 2017-2018 Savoir-faire Linux
# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    reference_ids = fields.One2many(
        'res.partner.reference', 'partner_id', copy=False)
