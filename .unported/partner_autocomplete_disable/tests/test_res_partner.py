# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data
from unittest import mock
from odoo.tests import common


@ddt
class TestResPartner(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_1")

    @data("konvergo", "odoo", "something", "google.com", "")
    def test_rpc_remote_api(self, query):
        with mock.patch("odoo.addons.iap.jsonrpc") as mocked:
            res = self.partner._rpc_remote_api("search", {"query": query})
            assert mocked.call_count == 0
            assert res == ({}, False)

    @data("konvergo", "odoo", "something", "google.com", "")
    def test_autocomplete(self, query):
        with mock.patch("odoo.addons.iap.jsonrpc") as mocked:
            assert self.partner.autocomplete(query) == []
            assert mocked.call_count == 0

    @data("konvergo", "odoo", "something", "google.com", "")
    def test_enrich_company(self, name):
        with mock.patch("odoo.addons.iap.jsonrpc") as mocked:
            assert self.partner.enrich_company(name, 123, "U12345678") == {}
            assert mocked.call_count == 0

    @data(
        "U12345678",
        "1234567890",
        "12345678901",
        "12345678X",
        "XX123456789",
        ""
    )
    def test_read_by_vat(self, vat):
        with mock.patch("odoo.addons.iap.jsonrpc") as mocked:
            assert self.partner.read_by_vat(vat) == []
            assert mocked.call_count == 0


class TestResPartnerAutocompleteSync(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.partner.vat = "XX123456789"
        self.autocomplete_sync = self.env["res.partner.autocomplete.sync"].create({
            "partner_id": self.partner.id,
            "synched": False
        })

    def test_whenStartSync_thenPatchedMethodIsCalled(self):
        """ make sure the targeted method is called during the process
        """
        module_memory_address = (
            "odoo.addons.partner_autocomplete_disable.res_partner.ResPartnerAutocompleteDisable"
        )
        with mock.patch(".".join([module_memory_address, "_rpc_remote_api"])) as mocked:
            autocomplete_module_memory_address = (
                "odoo.addons.partner_autocomplete.models.res_partner.ResPartner"
            )
            mocked.return_value = {}, False
            with mock.patch(".".join([autocomplete_module_memory_address, "_is_vat_syncable"])) as sync:
                sync.return_value = True
                self.autocomplete_sync.start_sync()
                assert mocked.call_count == 1

    def test_whenStartSync_noDataAreSent(self):
        with mock.patch("odoo.addons.iap.jsonrpc") as mocked:
            self.autocomplete_sync.start_sync()
            assert mocked.call_count == 0
