# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env["res.partner"].create(
            {"name": "Parent", "is_company": True, }
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "Contact",
                "parent_id": cls.parent.id,
            }
        )
        cls.user = cls.env.ref("base.user_demo")

    def test_manager_propagated_to_contact(self):
        self.parent.account_manager_id = self.user
        self.assertEqual(self.contact.account_manager_id, self.user)
