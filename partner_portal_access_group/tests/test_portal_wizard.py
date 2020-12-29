# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import AccessError


class TestResPartner(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.group = self.env.ref("partner_portal_access_group.group_portal_access")
        self.partner = self.env.ref("base.res_partner_1")

        self.wizard = self.env["portal.wizard"].create(
            {
                "user_ids": [(0, 0, {
                    "partner_id": self.partner.id,
                })]
            })

    def test_user_with_access(self):
        self.env.user.groups_id = self.group
        self.wizard.action_apply()

    def test_user_with_no_access(self):
        self.env.user.groups_id -= self.group
        with pytest.raises(AccessError):
            self.wizard.action_apply()
