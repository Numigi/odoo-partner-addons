# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common, Form


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        # Test using the demo user to prevent bugs related with access rights.
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_1 = cls.env['res.partner'].create({
            'firstname': 'Individual',
            'lastname': 'Partner',
            'company_type': 'person',
        })

    def test_no_warning_name_no_firstname_company_type_person(self):
        partner_2 = self.env['res.partner'].new(
            {
                'lastname': 'Customer',
                'firstname': '',
                'company_type': 'person',
            })
        onchange_result = partner_2._onchange_name_find_duplicates()
        self.assertFalse(
            isinstance(onchange_result, dict)
            and onchange_result.get("warning")
            or False
        )

    def test_no_warning_name_no_lastname_company_type_person(self):
        partner_3 = self.env['res.partner'].new(
            {
                'firstname': 'Individual',
                'lastname': '',
                'company_type': 'person',
            })
        onchange_result = partner_3._onchange_name_find_duplicates()
        self.assertFalse(
            isinstance(onchange_result, dict)
            and onchange_result.get("warning")
            or False
        )

    def test_warning_company_type_company(self):
        partner_4 = self.env['res.partner'].new(
            {
                'name': 'Individual Company',
                'company_type': 'company',
            })
        onchange_result = partner_4._onchange_name_find_duplicates()
        self.assertFalse(
            isinstance(onchange_result, dict)
            and onchange_result.get("warning")
            or False
        )
