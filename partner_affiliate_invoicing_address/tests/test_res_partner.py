# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from ..models.res_partner import INVOICE


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env["res.partner"].create(
            {
                "name": "Parent",
                "is_company": True,
            }
        )
        cls.parent_address = cls.env["res.partner"].create(
            {
                "name": "Invoicing Address 1",
                "type": INVOICE,
                "parent_id": cls.parent.id,
            }
        )

        cls.parent_address_2 = cls.env["res.partner"].create(
            {
                "name": "Invoicing Address 2",
                "type": INVOICE,
                "parent_id": cls.parent.id,
            }
        )

        cls.affiliate = cls.env["res.partner"].create(
            {
                "name": "Affiliate",
                "is_company": True,
                "parent_id": cls.parent.id,
            }
        )
        cls.affiliate_contact = cls.env["res.partner"].create(
            {
                "name": "Contact",
                "type": "contact",
                "parent_id": cls.affiliate.id,
            }
        )

    def test_box_not_checked(self):
        assert self.affiliate.address_get([INVOICE])[INVOICE] == self.affiliate.id

    def test_box_checked(self):
        self.affiliate.use_parent_invoice_address = True
        assert self.affiliate.address_get([INVOICE])[INVOICE] == self.parent_address.id

    def test_box_checked_and_choice_on_invoice_address_made_for_sale(self):
        self.affiliate.use_parent_invoice_address = True
        assert not self.affiliate.invoice_address_to_use_id
        self.affiliate.invoice_address_to_use_id = self.parent_address_2.id
        self.affiliate._onchange_use_parent_invoice_address()
        assert not self.affiliate.invoice_address_to_use_id
        assert self.affiliate.commercial_partner_id
        self.affiliate.commercial_partner_id.invoice_address_to_use_id = (
            self.parent_address_2.id
        )
        assert self.affiliate.commercial_partner_id.invoice_address_to_use_id
        assert (
            self.affiliate.address_get([INVOICE])[INVOICE] == self.parent_address_2.id
        )

    def test_invoice_address_not_asked(self):
        self.affiliate.use_parent_invoice_address = True
        res = self.affiliate.address_get()
        assert INVOICE not in res

    def test_contact_of_affiliate(self):
        self.affiliate.use_parent_invoice_address = True
        assert (
            self.affiliate_contact.address_get([INVOICE])[INVOICE]
            == self.parent_address.id
        )
