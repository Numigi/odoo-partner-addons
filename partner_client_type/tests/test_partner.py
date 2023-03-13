# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_type = cls.env["client.type"].create({"name": "Type A"})
        cls.parent = cls.env["res.partner"].create(
            {
                "name": "Parent",
                "is_company": True,
            }
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "Contact",
                "parent_id": cls.parent.id,
            }
        )

    def test_client_type_propagated_to_contact(self):
        self.parent.client_type_ids = self.client_type
        assert self.contact.client_type_ids == self.client_type
