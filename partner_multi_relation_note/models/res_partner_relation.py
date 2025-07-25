# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRelationWithNote(models.Model):

    _inherit = 'res.partner.relation'

    note = fields.Text('Note')
