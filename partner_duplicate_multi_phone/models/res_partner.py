# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
from odoo import _, api, fields, models

import re


class ResPartner(models.Model):

    _inherit = 'res.partner'

    mobile_indexed = fields.Char(
        compute='_compute_mobile_indexed', index=True, store=True)
    phone_home_indexed = fields.Char(
        compute='_compute_phone_home_indexed', index=True, store=True)
    phone_indexed = fields.Char(
        compute='_compute_phone_indexed', index=True, store=True)
    phone_other_indexed = fields.Char(
        compute='_compute_phone_other_indexed', index=True, store=True)

    def _onchange_phone_number(self, number, extension=None):
        number = _generate_phone_indexed_value(number, extension)
        duplicates = self._get_duplicates_by_phone(number)

        if duplicates:
            return {
                'warning': {
                    'title': 'Warning',
                    'message': _(
                        "This partner ({new_partner}) might be a duplicate "
                        "of the following partners: "
                        "\n\n\t{partner_names}.\n\n\t "
                        "These partners have identical phone numbers ({number})."
                    ).format(
                        new_partner=self.display_name,
                        partner_names="\n\t".join([p.display_name for p in duplicates]),
                        number=number
                    )
                }
            }

    @api.onchange('phone', 'phone_extension')
    def _onchange_phone_country(self):
        return self._onchange_phone_number(self.phone, self.phone_extension)

    @api.onchange('mobile')
    def _onchange_mobile_country(self):
        return self._onchange_phone_number(self.mobile)

    @api.onchange('phone_home')
    def _onchange_phone_home_country(self):
        return self._onchange_phone_number(self.phone_home)

    @api.onchange('phone_other', 'phone_other_extension')
    def _onchange_phone_other_country(self):
        return self._onchange_phone_number(self.phone_other, self.phone_other_extension)

    @api.depends('phone', 'phone_extension')
    def _compute_phone_indexed(self):
        for record in self:
            record.phone_indexed = _generate_phone_indexed_value(
                record.phone, record.phone_extension)

    @api.depends('phone_other', 'phone_other_extension')
    def _compute_phone_other_indexed(self):
        for record in self:
            record.phone_other_indexed = _generate_phone_indexed_value(
                record.phone_other, record.phone_other_extension)

    @api.depends('mobile')
    def _compute_mobile_indexed(self):
        for record in self:
            record.mobile_indexed = _generate_phone_indexed_value(record.mobile)

    @api.depends('phone_home')
    def _compute_phone_home_indexed(self):
        for record in self:
            record.phone_home_indexed = _generate_phone_indexed_value(record.phone_home)

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

        return self.env['res.partner'].browse([r[0] for r in cr.fetchall()])

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

    def _search_for_duplicates(self, vals):
        res = self.env['res.partner']

        if vals.get('phone_home'):
            res |= self._create_phone_duplicates(self.phone_home_indexed)

        if vals.get('mobile'):
            res |= self._create_phone_duplicates(self.mobile_indexed)

        if vals.get('phone') or vals.get('phone_extension'):
            res |= self._create_phone_duplicates(self.phone_indexed)

        if vals.get('phone_other') or vals.get('phone_other_extension'):
            res |= self._create_phone_duplicates(self.phone_other_indexed)

        return res

    def _post_message_phone_duplicates(self, duplicates):
        for record in self:
            if duplicates:
                message = _(
                    'Duplicate partners found (with the same phone number): {partners}'
                ).format(partners=', '.join(duplicates.mapped('name')))
                record.message_post(body=message)

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for record in self:
            duplicates = record._search_for_duplicates(vals)
            record._post_message_phone_duplicates(duplicates)
        return res

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        duplicates = res._search_for_duplicates(vals)
        res._post_message_phone_duplicates(duplicates)
        return res


def _generate_phone_indexed_value(phone, extension=None):
    """Generate a concatenated phone number with the extension.

    This function is used to create an indexedable string containing
    the whole number of a contact.

    :param phone: a phone number string
    :param extension: a phone extension string
    :return: the concatenated phone and extension string
    """
    if phone is None:
        phone = ''

    if extension is None:
        extension = ''

    number = '{phone}{extension}'.format(phone=phone, extension=extension)
    return (''.join(c for c in number if c.isdigit()))
