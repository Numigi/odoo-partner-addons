# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class IrModelFields(models.Model):

    _inherit = 'ir.model.fields'

    @api.multi
    def name_get(self):
        if not self.env.context.get('special_display_name'):
            return super(IrModelFields, self).name_get()

        res = []
        for field in self:
            res.append((field.id, '%s' % (field.field_description,)))

        return res
