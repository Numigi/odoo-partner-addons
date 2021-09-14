# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.api import Environment
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import common


class TestResPartnerChangeParent(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartnerChangeParent, cls).setUpClass()

        cls.user = cls.env.ref("base.user_demo")

        cls.internal_user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test.user@example.com",
                "email": "test.user@example.com",
            }
        )

        # Test using the demo user to prevent bugs related with access rights.
        cls.env = Environment(cls.env.cr, cls.user.id, {})

        cls.company_1 = cls.env["res.partner"].create(
            {"name": "Company 1", "is_company": True}
        )
        cls.company_2 = cls.env["res.partner"].create(
            {"name": "Company 2", "is_company": True}
        )

        cls.contact_1_email = "test1@localhost"
        cls.contact_1 = cls.env["res.partner"].create(
            {
                "name": "Contact 1",
                "is_company": False,
                "email": cls.contact_1_email,
                "parent_id": cls.company_1.id,
            }
        )

    def test_new_contact_is_not_the_old_contact(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        assert len(new_contact) == 1
        assert new_contact != self.contact_1

    def test_email_propagation_to_new_contact(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        assert new_contact.email == self.contact_1_email

    def test_old_contact_is_archived(self):
        self._run_partner_change_wizard(self.contact_1, self.company_2)
        assert not self.contact_1.active

    def test_new_contact_has_destination_parent(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        assert new_contact.parent_id == self.company_2

    def test_old_contact_is_still_under_the_original_parent(self):
        self._run_partner_change_wizard(self.contact_1, self.company_2)
        assert self.contact_1.parent_id == self.company_1

    def test_no_destination_parent(self):
        new_contact = self._run_partner_change_wizard(self.contact_1, None)
        assert not new_contact.parent_id

    def test_no_source_parent(self):
        contact_with_no_company = self.env["res.partner"].create(
            {
                "name": "Contact With No Company",
                "is_company": False,
                "email": "test2@localhost",
                "parent_id": False,
            }
        )
        new_contact = self._run_partner_change_wizard(
            contact_with_no_company, self.company_1
        )
        assert new_contact.parent_id, self.company_1

    def test_destination_parent_with_address(self):
        """Test that the address is changed when changing the parent company."""
        assert not self.contact_1.city
        self.company_1.city = "New York"
        self.contact_1.refresh()
        assert self.contact_1.city == "New York"

        self.company_2.city = "Los Angeles"
        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        assert new_contact.city == "Los Angeles"

    def test_destination_parent_with_no_address(self):
        """Test that the address is removed if the destination company has no address."""
        assert not self.contact_1.city
        self.company_1.city = "New York"
        self.contact_1.refresh()
        assert self.contact_1.city == "New York"

        new_contact = self._run_partner_change_wizard(self.contact_1, self.company_2)
        assert not new_contact.city

    def test_if_user_bound_to_portal_user__raise_validation_error(self):
        contact = self.env.ref("base.partner_demo_portal")
        with self.assertRaises(ValidationError):
            self._run_partner_change_wizard(contact, self.company_2)

    def test_if_portal_user_archived__parent_company_changed(self):
        contact = self.env.ref("base.partner_demo_portal")
        contact.user_ids.sudo().active = False
        new_contact = self._run_partner_change_wizard(contact, self.company_2)
        assert new_contact.parent_id == self.company_2

    def test_correction_of_parent_company(self):
        new_contact = self._run_partner_change_wizard(
            self.contact_1, self.company_2, is_correction=True
        )
        assert not new_contact
        assert self.contact_1.active
        assert self.contact_1.parent_id == self.company_2

    def _run_partner_change_wizard(
        self, contact, destination_company=None, is_correction=False
    ):
        wizard = (
            self.env["res.partner.change.parent"]
            .with_context(
                {
                    "active_id": contact.id,
                    "active_model": "res.partner",
                }
            )
            .create(
                {
                    "new_company_id": destination_company.id
                    if destination_company
                    else None,
                    "is_correction": is_correction,
                }
            )
        )
        wizard.validate()
        return wizard.new_contact_id
