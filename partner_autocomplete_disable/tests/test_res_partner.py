# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock
from odoo.tests import common


class TestResPartner(common.TransactionCase):

    def test_autocomplete(self):
        partner = self.env.ref("base.res_partner_1")
        with mock.patch.object(partner, "_rpc_remote_api") as mocked:
            partner.autocomplete("konvergo")
            assert mocked.call_count == 0
