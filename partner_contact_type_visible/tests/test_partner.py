# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from ddt import ddt, data
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


@ddt
class TestPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env["res.partner"].create(
            {"name": "Parent", "is_company": True,}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Contact",
                "type": "contact",
            }
        )

    @data(
        "invoice",
        "delivery",
        "other",
    )
    def test_address_with_no_parent(self, partner_type):
        with pytest.raises(ValidationError):
            self.partner.type = partner_type

    @data(
        "invoice",
        "delivery",
        "other",
    )
    def test_address_with_parent(self, partner_type):
        self.partner.parent_id = self.parent
        self.partner.type = partner_type
