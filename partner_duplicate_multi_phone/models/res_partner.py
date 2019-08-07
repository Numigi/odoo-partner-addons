# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
from odoo import _, api, fields, models


class ResPartnerWithIndexedPhones(models.Model):
    """Add indexed phone columns on partners.

    The new columns are required to run the phone comparisons quickly.

    The values stored in the indexed columns are the phone numbers
    without any formating, so that a phone such as 1-450-222-3333 on a
    partner will match +1 (450) 222-3333 on another.
    """

    _inherit = 'res.partner'

    mobile_indexed = fields.Char(
        compute='_compute_mobile_indexed', index=True, store=True)
    phone_home_indexed = fields.Char(
        compute='_compute_phone_home_indexed', index=True, store=True)
    phone_indexed = fields.Char(
        compute='_compute_phone_indexed', index=True, store=True)
    phone_other_indexed = fields.Char(
        compute='_compute_phone_other_indexed', index=True, store=True)

    @api.depends('phone')
    def _compute_phone_indexed(self):
        for record in self:
            record.phone_indexed = generate_phone_indexed_value(record.phone)

    @api.depends('phone_other')
    def _compute_phone_other_indexed(self):
        for record in self:
            record.phone_other_indexed = generate_phone_indexed_value(record.phone_other)

    @api.depends('mobile')
    def _compute_mobile_indexed(self):
        for record in self:
            record.mobile_indexed = generate_phone_indexed_value(record.mobile)

    @api.depends('phone_home')
    def _compute_phone_home_indexed(self):
        for record in self:
            record.phone_home_indexed = generate_phone_indexed_value(record.phone_home)

    @api.onchange('phone')
    def _onchange_phone_country(self):
        return self._onchange_phone_number(self.phone)

    @api.onchange('mobile')
    def _onchange_mobile_country(self):
        return self._onchange_phone_number(self.mobile)

    @api.onchange('phone_home')
    def _onchange_phone_home_country(self):
        return self._onchange_phone_number(self.phone_home)

    @api.onchange('phone_other')
    def _onchange_phone_other_country(self):
        return self._onchange_phone_number(self.phone_other)

    def _onchange_phone_number(self, number):
        number = generate_phone_indexed_value(number)
        duplicates = self._get_duplicates_by_phone(number)

        if duplicates:
            return {
                'warning': {
                    'title': 'Warning',
                    'message': _(
                        "This partner ({new_partner}) might be a duplicate "
                        "of the following partners: "
                        "\n\n{partner_names}\n\n "
                        "These partners have identical phone numbers ({number})."
                    ).format(
                        new_partner=self.display_name,
                        partner_names="\n".join([p.display_name for p in duplicates]),
                        number=number
                    )
                }
            }

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for record in self:
            duplicates = record._search_for_duplicates(vals)
            if duplicates:
                record._post_message_phone_duplicates(duplicates)
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        duplicates = res._search_for_duplicates(vals)
        if duplicates:
            res._post_message_phone_duplicates(duplicates)
        return res

    def _search_for_duplicates(self, vals):
        res = self.env['res.partner']

        if vals.get('phone_home'):
            res |= self._create_phone_duplicates(self.phone_home_indexed)

        if vals.get('mobile'):
            res |= self._create_phone_duplicates(self.mobile_indexed)

        if vals.get('phone'):
            res |= self._create_phone_duplicates(self.phone_indexed)

        if vals.get('phone_other'):
            res |= self._create_phone_duplicates(self.phone_other_indexed)

        return res

    def _create_phone_duplicates(self, phone):
        partners = self._get_duplicates_by_phone(phone)
        if partners:
            records = self.env['res.partner.duplicate']
            for partner in partners:
                records |= self.env['res.partner.duplicate'].create({
                    'partner_1_id': self.id,
                    'partner_2_id': partner.id,
                })
            return partners

        return self.env['res.partner']

    def _post_message_phone_duplicates(self, duplicates):
        for record in self:
            message = _(
                'Duplicate partners found (with the same phone number): {partners}'
            ).format(partners=', '.join(duplicates.mapped('name')))
            record.message_post(body=message)

    def _get_duplicates_by_phone(self, phone):
        """Get existing partner duplicates given a phone number.

        The given phone number can match any of the following phones:
            * Home (phone_home_indexed)
            * Mobile (mobile_indexed)
            * Work (phone_indexed)
            * Other (phone_other_indexed)

        :param self: the partner for which to find duplicates
        :param phone: the phone number to use for finding duplicates
        :return: a record set of duplicate partners
        """
        if self._context.get('disable_duplicate_check'):
            return self.env['res.partner']

        if not phone:
            return self.env['res.partner']

        cr = self.env.cr
        cr.execute("""
            SELECT p.id
            FROM res_partner p
            WHERE p.id != %(id)s
            AND p.active = true
            AND (
                p.phone_home_indexed = %(phone)s
                OR p.mobile_indexed = %(phone)s
                OR p.phone_indexed = %(phone)s
                OR p.phone_other_indexed = %(phone)s
            )
            AND NOT EXISTS (
                SELECT NULL
                FROM res_partner_duplicate d
                WHERE (d.partner_1_id = p.id AND d.partner_2_id = %(id)s)
                OR    (d.partner_1_id = %(id)s AND d.partner_2_id = p.id)
            )

        """, {
            'id': self.id or self._origin.id or 0,
            'phone': phone,
        })

        duplicate_partners = self.env['res.partner'].browse([r[0] for r in cr.fetchall()])
        exclude_parents_and_children = (lambda p: p.parent_id != self and self.parent_id != p)
        return duplicate_partners.filtered(exclude_parents_and_children)


def generate_phone_indexed_value(phone):
    """Generate a phone string to index for search index comparison.

    :param phone: a phone number string
    :return: a phone number string
    """
    return (''.join(c for c in phone if c.isdigit())) if phone else None
