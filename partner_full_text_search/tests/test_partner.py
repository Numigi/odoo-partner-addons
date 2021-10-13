# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import data, ddt, unpack
from odoo.tests import common


@ddt
class TestPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env["res.partner"].create({
            "name": "Société au Québec",
        })
        cls.partner_1 = cls.env["res.partner"].create({
            "name": "Bien-Être En Été",
            "parent_id": cls.parent.id,
        })
        cls.partner_2 = cls.env["res.partner"].create({
            "name": "Bien Froid En Hivers",
            "parent_id": cls.parent.id,
        })

    @data(
        "bien-être",
        "bien-etre",
        "bien etre",
        "Bien Être",
        "En-ete",
    )
    def test_search(self, name):
        res = self._search(name)
        assert self.partner_1 in res

    def test_partner_not_duplicate(self):
        res = self._search(self.partner_1.name)
        count = len(res.filtered(lambda p: p == self.partner_1))
        assert count == 1

    def test_search_limit(self):
        res = self._search("Bien En", limit=1)
        assert len(res) == 1

    def test_search_domain(self):
        res = self._search("Bien En", domain=[("id", "=", self.partner_1.id)])
        assert res == self.partner_1

    @data(
        ("418 555-6666", "4185556666"),
        ("+1 418-555-6666", "4185556666"),
        ("+1 418-555-6666", "+1 418-555-6666"),
    )
    @unpack
    def test_search_by_phone_number(self, partner_phone, text):
        self.partner_1.phone = partner_phone
        self.partner_1.refresh()
        print(self.partner_1.phone)
        res = self._search(text)
        assert self.partner_1 in res

    def test_search_by_mobile_phone_number(self):
        self.partner_1.mobile = "418 555-6666"
        res = self._search("4185556666")
        assert self.partner_1 in res

    def test_search_by_email(self):
        self.partner_1.email = "john-doe.1@example"
        res = self._search("john doe")
        assert self.partner_1 in res

    def test_search_by_street(self):
        self.partner_1.street = "10000 rue du Belvédère"
        res = self._search("belvedere")
        assert self.partner_1 in res

    def test_search_by_ref(self):
        self.partner_1.ref = "ABC-LTÉE"
        res = self._search("abc ltee")
        assert self.partner_1 in res

    def test_search_by_parent_name(self):
        self.parent.name = "Montréal Inc."
        res = self._search("Montreal")
        assert self.parent in res
        assert self.partner_1 in res

    def _search(self, name, operator="ilike", domain=None, limit=None):
        items = self.env["res.partner"].name_search(
            name, args=domain, operator=operator, limit=limit or 999999
        )
        return self.env["res.partner"].browse([el[0] for el in items])
