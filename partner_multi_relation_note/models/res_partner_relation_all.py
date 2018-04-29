# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerRelationAllWithNote(models.AbstractModel):

    _inherit = 'res.partner.relation.all'

    note = fields.Text('Note')

    def _get_additional_relation_columns(self):
        additional_columns = super()._get_additional_relation_columns()
        return ', '.join((additional_columns, 'note'))
