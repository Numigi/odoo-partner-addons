# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestResPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.email = "some.email@localhost"

        cls.parent_partner = cls.env["res.partner"].create(
            {"name": "Parent Partner", "is_company": True}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner",
                "type": "contact",
                "email": cls.email,
                "parent_id": cls.parent_partner.id,
            }
        )

    def test_create_user_with_same_email(self):
        user = self._create_user(self.email)
        assert user.partner_id == self.partner

    def test_partner_fields_not_overriden(self):
        user = self._create_user(self.email, parent_id=False)
        assert user.partner_id == self.partner
        assert user.partner_id.parent_id == self.parent_partner

    def test_create_user_with_different_email(self):
        user = self._create_user("other.email@localhost")
        assert user.partner_id and user.partner_id != self.partner

    def test_create_user_with_archived_partner(self):
        self.partner.active = False
        with pytest.raises(ValidationError):
            self._create_user(self.email)

    def test_partner_already_assigned_to_a_user(self):
        self._create_user(self.email)
        with pytest.raises(ValidationError):
            self._create_user(self.email)

    def _create_user(self, email, **kwargs):
        return self.env["res.users"].create(
            {"email": email, "name": email, "login": email, **kwargs}
        )
