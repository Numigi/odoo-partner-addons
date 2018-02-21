# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class IrModelFields(models.Model):

    _inherit = 'ir.model.fields'

    @api.multi
    def name_get(self):
        if not self._context.get('no_display_model_name'):
            return super(IrModelFields, self).name_get()

        return [(f.id, f.field_description) for f in self]
