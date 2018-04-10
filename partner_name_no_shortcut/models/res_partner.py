# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re

from odoo import api, models

PARTNER_NAME_FIELDS = ('firstname', 'lastname', 'name')


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        super().write(vals)
        if any(f in vals for f in PARTNER_NAME_FIELDS):
            self._remove_shortcuts_from_partner_name()
        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._remove_shortcuts_from_partner_name()
        return res

    def _remove_shortcuts_from_partner_name(self):
        """Remove business type and title shortcuts from the partner name fields."""
        titles = get_shortcut_list(self.env['res.partner.title'])
        business_types = get_shortcut_list(self.env['res.partner.business.type'])
        terms_to_exclude = titles + business_types

        cleaner = PartnerNameCleaner(PARTNER_NAME_FIELDS, terms_to_exclude)

        for partner in self:
            cleaner.clean(partner)


def get_shortcut_list(model_cls):
    """Get a complete list of shorcuts including the translated values.

    :param model_cls: the class of the model for which to find shortcuts
    :return: a list of terms
    """
    res = model_cls.search([]).mapped('shortcut')
    translations = model_cls.env['ir.translation'].search([
        ('type', '=', 'model'),
        ('name', '=', '{model},shortcut'.format(model=model_cls._name)),
    ])
    res.extend(translations.mapped('value'))
    res.extend(translations.mapped('src'))
    return list(set(res))


class PartnerNameCleaner:
    """A class responsible for removing terms from partner names."""

    def __init__(self, fields_to_clean, terms_to_exclude):
        """Initialize the name cleaner.

        :param terms_to_exclude: a list of strings that must be excluded from the partner name.
        """
        self._fields_to_clean = fields_to_clean
        self._terms_to_exclude_regex_list = self._build_regex_list(terms_to_exclude)

    @staticmethod
    def _build_regex_list(terms_to_exclude):
        """Build a list of string replacement regex.

        Each regex attempts to match the given term as a complete word.

        Either the term to match is:

        * at the begging of the string (usually, partner titles are before the name)
        * at the end of the string (usually, business types are after the name)

        :param terms_to_exclude: a list of strings that must be excluded from the partner name.
        :return: a list of string replacement regex
        """
        # Strip terms
        terms_to_exclude = [t.strip() for t in terms_to_exclude]

        # Remove leading dots
        no_leading_dots_regex = re.compile('\\.$')
        terms_to_exclude = [no_leading_dots_regex.sub('', t) for t in terms_to_exclude]

        # Escape terms before computing the regex list
        terms_to_exclude = [re.escape(t) for t in terms_to_exclude]

        return [
            re.compile('^\s*{term}\\.?\s+|\s+{term}\\.?\s*$'.format(term=t), re.IGNORECASE)
            for t in terms_to_exclude
        ]

    def clean(self, partner):
        """Clean the name fields of a partner.

        :param partner: the partner to clean.
        """
        name_fields_set_on_partner = (
            f for f in self._fields_to_clean
            if f in partner._fields and partner[f]
        )

        for field_name in name_fields_set_on_partner:
            value_before = partner[field_name]
            value_after = self._remove_terms_from_string(value_before)
            if value_before != value_after:
                partner.write({field_name: value_after})

    def _remove_terms_from_string(self, string):
        """Remove all matching terms from the given string.

        :param string: the string to clean
        """
        for regex in self._terms_to_exclude_regex_list:
            match = regex.search(string)
            if match is not None:
                string = regex.sub('', string)
        return string
