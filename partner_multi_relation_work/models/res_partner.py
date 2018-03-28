# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        """Automatically create a work relation when creating a contact.

        When creating a contact, if it has a company as parent, automatically
        create a work relation between the company and the contact.
        """
        res = super().create(vals)
        if res.parent_id.is_company:
            self.env['res.partner.relation'].create({
                'left_partner_id': res.id,
                'right_partner_id': res.parent_id.id,
                'type_id': self.env.ref('partner_multi_relation_work.relation_type_work').id,
                'date_start': fields.Date.context_today(self),
            })
        return res
