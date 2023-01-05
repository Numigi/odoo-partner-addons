# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from ..models.res_partner import INVOICE


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env["res.partner"].create(
            {"name": "Parent", "is_company": True,}
        )
        cls.parent_address = cls.env["res.partner"].create(
            {
                "name": "Invoicing Address",
                "type": INVOICE,
                "parent_id": cls.parent.id,
            }
        )
        cls.affiliate = cls.env["res.partner"].create(
            {"name": "Affiliate", "is_company": True, "parent_id": cls.parent.id,}
        )
        cls.affiliate_contact = cls.env["res.partner"].create(
            {"name": "Contact", "type": "contact", "parent_id": cls.affiliate.id,}
        )

    def test_box_not_checked(self):
        assert self.affiliate.address_get([INVOICE])[INVOICE] == self.affiliate.id

    def test_box_checked(self):
        self.affiliate.use_parent_invoice_address = True
        assert self.affiliate.address_get([INVOICE])[INVOICE] == self.parent_address.id

    def test_invoice_address_not_asked(self):
        self.affiliate.use_parent_invoice_address = True
        res = self.affiliate.address_get()
        assert INVOICE not in res

    def test_contact_of_affiliate(self):
        self.affiliate.use_parent_invoice_address = True
        assert self.affiliate_contact.address_get([INVOICE])[INVOICE] == self.parent_address.id
