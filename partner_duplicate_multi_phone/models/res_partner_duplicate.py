# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerDuplicate(models.Model):

    _inherit = 'res.partner.duplicate'

    partner_1_type = fields.Selection(related='partner_1_id.company_type')
    partner_2_type = fields.Selection(related='partner_2_id.company_type')

    def _find_partner_duplicates(self):
        res = super(ResPartnerDuplicate, self)._find_partner_duplicates()

        self.env.cr.execute("""
            SELECT p1.id, p2.id
            FROM res_partner p1, res_partner p2
            WHERE p1.id != p2.id
            AND p1.active = true
            AND p2.active = true
            AND (
                p1.phone_home_indexed is not NULL AND (
                    p1.phone_home_indexed = p2.phone_home_indexed
                    OR p1.phone_home_indexed = p2.mobile_indexed
                    OR p1.phone_home_indexed = p2.phone_indexed
                    OR p1.phone_home_indexed = p2.phone_other_indexed
                )
                OR p1.mobile_indexed is not NULL AND (
                    p1.mobile_indexed = p2.phone_home_indexed
                    OR p1.mobile_indexed = p2.mobile_indexed
                    OR p1.mobile_indexed = p2.phone_indexed
                    OR p1.mobile_indexed = p2.phone_other_indexed
                )
                OR p1.phone_indexed is not NULL AND (
                    p1.phone_indexed = p2.phone_home_indexed
                    OR p1.phone_indexed = p2.mobile_indexed
                    OR p1.phone_indexed = p2.phone_indexed
                    OR p1.phone_indexed = p2.phone_other_indexed
                )
                OR p1.phone_other_indexed is not NULL AND (
                    p1.phone_other_indexed = p2.phone_home_indexed
                    OR p1.phone_other_indexed = p2.mobile_indexed
                    OR p1.phone_other_indexed = p2.phone_indexed
                    OR p1.phone_other_indexed = p2.phone_other_indexed
                )
            )
            AND NOT EXISTS (
                SELECT NULL
                FROM res_partner_duplicate d
                WHERE (d.partner_1_id = p1.id AND d.partner_2_id = p2.id)
                OR    (d.partner_1_id = p2.id AND d.partner_2_id = p1.id)
            )
        """)

        return res + self.env.cr.fetchall()
