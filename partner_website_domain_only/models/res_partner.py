# -*- coding: utf-8 -*-
# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from werkzeug import urls

from odoo import models


class ResPartnerWebsiteWithDomainOnly(models.Model):
    """Remove any part after the domain on website."""

    _inherit = 'res.partner'

    def _clean_website(self, website):
        website_with_scheme = super()._clean_website(website)
        return self._remove_parts_after_domain_from_website(website_with_scheme)

    @staticmethod
    def _remove_parts_after_domain_from_website(website):
        """Remove the path, the query and the fragment from the given website url.

        :param website: a website url string
        :return: a website url string with no fragment and no query
        """
        url = urls.url_parse(website)
        url_with_domain_only = url.replace(path='', fragment='', query='')
        return url_with_domain_only.to_url()
