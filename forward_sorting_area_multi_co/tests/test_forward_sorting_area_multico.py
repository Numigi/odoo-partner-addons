# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.test_mail.tests.common import mail_new_test_user

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import common
from odoo.tools import mute_logger
from psycopg2 import IntegrityError


class TestFSAMultiCo(common.TransactionCase):
    def setUp(self):
        super(TestFSAMultiCo, self).setUp()
        self.company_1 = self.env["res.company"].create(
            {
                "name": "Test company 1",
            }
        )
        self.company_2 = self.env["res.company"].create(
            {
                "name": "Test company 2",
            }
        )

        self.user_1 = mail_new_test_user(
            self.env,
            login="user_test_1",
            email="user_test_1@example.com",
            groups="base.group_user,base.group_partner_manager",
        )

        self.user_2 = mail_new_test_user(
            self.env,
            login="user_test_2",
            email="user_test_2@example.com",
            groups="base.group_user,base.group_partner_manager",
        )

        self.user_1.write(
            {
                "company_id": self.company_1.id,
                "company_ids": [(6, 0, [self.company_1.id])],
            }
        )
        self.user_2.write(
            {
                "company_id": self.company_2.id,
                "company_ids": [(6, 0, [self.company_2.id])],
            }
        )
        # user_1 create Territory 1
        self.territory_1 = (
            self.env["res.territory"]
            .sudo(self.user_1.id)
            .create(
                {
                    "name": "Territory 1",
                }
            )
        )

        # user_2 create Territory 2
        self.territory_2 = (
            self.env["res.territory"]
            .sudo(self.user_2.id)
            .create(
                {
                    "name": "Territory 2",
                }
            )
        )

        # user_1 create FSA 1
        self.fsa_1 = (
            self.env["forward.sortation.area"]
            .sudo(self.user_1.id)
            .create(
                {
                    "name": "A1N",
                    "territory_ids": [(6, 0, [self.territory_1.id])],
                }
            )
        )

        # user_2 create FSA 2
        self.fsa_2 = (
            self.env["forward.sortation.area"]
            .sudo(self.user_2.id)
            .create(
                {
                    "name": "A1Z",
                }
            )
        )
        # user_1 create partner 1
        self.partner_1 = (
            self.env["res.partner"]
            .sudo(self.user_1.id)
            .create(
                {
                    "name": "Partner",
                    "zip": "A1NB2B",
                }
            )
        )

    def test_check_territory_company(self):
        assert self.territory_1.company_id == self.company_1
        assert self.territory_2.company_id == self.company_2

    def test_check_fsa_company(self):
        assert self.fsa_1.company_id == self.company_1
        assert self.fsa_2.company_id == self.company_2

    def test_access_territory_1_by_user_2(self):
        with self.assertRaises(AccessError):
            self.territory_1.sudo(self.user_2.id).read()

    def test_access_territory_2_by_user_1(self):
        with self.assertRaises(AccessError):
            self.territory_2.sudo(self.user_1.id).read()

    def test_access_fsa_1_by_user_2(self):
        with self.assertRaises(AccessError):
            self.fsa_1.sudo(self.user_2.id).read()

    def test_access_fsa_2_by_user_1(self):
        with self.assertRaises(AccessError):
            self.fsa_2.sudo(self.user_1.id).read()

    def test_fsa_partner_1_by_company1(self):
        assert self.partner_1.sudo(self.user_1.id).fsa_id == self.fsa_1

    def test_fsa_partner_1_by_company2(self):
        self.assertFalse(self.partner_1.sudo(self.user_2.id).fsa_id)

    @mute_logger("odoo.sql_db")
    def test_check_unique_FSAname_per_company(self):
        with self.assertRaises(IntegrityError):
            self.env["forward.sortation.area"].sudo(self.user_2.id).create(
                {
                    "name": "A1Z",
                }
            )

    @mute_logger("odoo.sql_db")
    def test_check_unique_Territory_name_per_company(self):
        with self.assertRaises(IntegrityError):
            self.env["res.territory"].sudo(self.user_1.id).create(
                {
                    "name": "Territory 1",
                }
            )

    def test_check_territory_ids(self):
        with self.assertRaises(ValidationError):
            self.territory_2.write({"company_id": self.company_1.id})

    def test_check_fsa_ids(self):
        with self.assertRaises(ValidationError):
            self.fsa_1.write({"company_id": self.company_2.id})
