# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ResPartnerTitle(models.Model):

    _inherit = 'res.partner.title'

    @api.model
    def get_shortcut_list(self):
        """Get a complete list of partner title shortcuts including the translated values.

        :return: a list of terms
        :rtype: list
        """
        res = self.search([]).mapped('shortcut')
        translations = self.env['ir.translation'].search([
            ('type', '=', 'model'),
            ('name', '=', 'res.partner.title,shortcut'),
        ])
        res.extend(translations.mapped('value'))
        res.extend(translations.mapped('src'))
        return res
