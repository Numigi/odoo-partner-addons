# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerDuplicateWithPhoneComparisons(models.Model):
    """Add phone comparisons to the cron to find duplicates."""

    _inherit = 'res.partner.duplicate'

    def _find_duplicate_partner_ids(self):
        """Find matching partner duplicates based on phone numbers.

        Any of the 4 phone types may match any other phone type.
        """
        res = super()._find_duplicate_partner_ids()

        def phone_comparison(phone_field):
            return """
                p1.{phone_field} is not NULL
                AND p1.{phone_field} != ''
                AND (
                    p1.{phone_field} = p2.phone_indexed
                    OR p1.{phone_field} = p2.mobile_indexed
                    OR p1.{phone_field} = p2.phone_home_indexed
                    OR p1.{phone_field} = p2.phone_other_indexed
                )
            """.format(phone_field=phone_field)

        query = """
            SELECT p1.id, p2.id
            FROM res_partner p1, res_partner p2
            WHERE p1.id != p2.id
            AND p1.active = true
            AND p2.active = true
            AND (
                {comparison_1}
                OR {comparison_2}
                OR {comparison_3}
                OR {comparison_4}
            )
            AND NOT EXISTS (
                SELECT NULL
                FROM res_partner_duplicate d
                WHERE (d.partner_1_id = p1.id AND d.partner_2_id = p2.id)
                OR    (d.partner_1_id = p2.id AND d.partner_2_id = p1.id)
            )
        """.format(
            comparison_1=phone_comparison('phone_indexed'),
            comparison_2=phone_comparison('mobile_indexed'),
            comparison_3=phone_comparison('phone_home_indexed'),
            comparison_4=phone_comparison('phone_other_indexed'),
        )

        self.env.cr.execute(query)
        return res + self.env.cr.fetchall()
