# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from odoo.api import Environment


class TestPartnerAffiliate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = cls.env.ref('base.user_root')
        cls.company = cls.env["res.partner"].create(
            {"name": "Parent", "is_company": True}
        )
        cls.company2 = cls.env["res.partner"].create(
            {"name": "Parent2", "is_company": True}
        )
        cls.affiliate = cls.env["res.partner"].create(
            {"name": "Affiliate", "is_company": True,
             "parent_id": cls.company.id}
        )
        cls.company.affiliate_ids = [(4, cls.affiliate.id)]
        cls.affiliate_contact = cls.env["res.partner"].create(
            {"name": "Contact", "type": "contact",
             "parent_id": cls.affiliate.id}
        )
        cls.affiliate.affiliate_ids = [(4, cls.affiliate_contact.id)]
        cls.env = Environment(cls.env.cr, cls.admin.id, {})

    def test_company_is_company_parent(self):
        assert self.company.is_company_parent == 1

    def test_affiliate_is_not_company_parent(self):
        assert self.affiliate.is_company_parent == 0

    def test_company_contact_parent_id(self):
        assert self.affiliate.highest_parent_id.id == self.company.id

    def test_affiliate_contact_parent_id(self):
        assert self.affiliate_contact.highest_parent_id.id == self.company.id

    def test_change_affiliate_parent_id(self):
        self.affiliate.write({'parent_id': self.company2.id})
        assert self.affiliate_contact.highest_parent_id.id == self.company2.id
