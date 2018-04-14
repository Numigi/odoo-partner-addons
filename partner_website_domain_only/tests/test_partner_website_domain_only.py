# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestPartnerWebsiteDomainOnly(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Partner'})

    def test_website_with_no_path(self):
        self.partner.website = 'https://www.odoo.com'
        self.partner.refresh()
        assert self.partner.website == 'https://www.odoo.com'

    def test_website_with_path(self):
        self.partner.website = 'https://www.odoo.com/page/tour'
        self.partner.refresh()
        assert self.partner.website == 'https://www.odoo.com'

    def test_website_with_query_string(self):
        self.partner.website = 'https://www.odoo.com?debug='
        self.partner.refresh()
        assert self.partner.website == 'https://www.odoo.com'

    def test_website_with_path_and_fragment(self):
        self.partner.website = 'https://www.odoo.com/page/tour#contact_us'
        self.partner.refresh()
        assert self.partner.website == 'https://www.odoo.com'
