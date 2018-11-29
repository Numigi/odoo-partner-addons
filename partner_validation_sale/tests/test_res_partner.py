# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import SavepointCase
from odoo.exceptions import Warning as WarningOdoo


class TestResPartner(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.group_sale_manager = cls.env.ref(
            'sales_team.group_sale_manager')
        cls.group_partner_restricted_field_sales = cls.env.ref(
            'partner_validation_sale.group_partner_restricted_field_sales')

        cls.normal_user = cls.env['res.users'].create({
            'name': 'Normal User',
            'login': 'normaluserlogin',
            'email': 'normaluser@test.com',
            'groups_id': [(6, 0, [
                cls.group_sale_manager.id,
            ])],
        })

        cls.customer_approval_user = cls.env['res.users'].create({
            'name': 'Controller Approval User',
            'login': 'controllerapprovaluserlogin',
            'email': 'controllerapprovaluser@test.com',
            'groups_id': [(6, 0, [
                cls.group_sale_manager.id,
                cls.group_partner_restricted_field_sales.id,
            ])],
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner Test',
            'is_company': True,
            'phone': '000-111-222',
            'email': 'partnertest@test.com',
            'customer': True,
            'customer_state': 'new'
        })

        partner_phone_field_id = cls.env.ref('base.field_res_partner_phone').id
        phone_vals = {
            'field_id': partner_phone_field_id,
            'apply_on_sales': True,
        }
        cls.env['res.partner.restricted.field'].create(phone_vals)

        partner_email_field_id = cls.env.ref('base.field_res_partner_email').id
        email_vals = {
            'field_id': partner_email_field_id,
            'apply_on_sales': False
        }
        cls.env['res.partner.restricted.field'].create(email_vals)

    def test_01_confirm_customer_with_normal_user(self):
        self.partner.sudo(self.normal_user).confirm_customer()
        self.assertEqual(self.partner.customer_state, 'confirmed')

    def test_02_approve_customer_with_normal_user(self):
        self.partner.sudo(self.normal_user).confirm_customer()
        with self.assertRaises(WarningOdoo):
            self.partner.sudo(self.normal_user).approve_customer()

    def test_03_reject_customer_with_normal_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        self.partner.sudo(self.normal_user).reject_customer()
        self.assertEqual(self.partner.customer_state, 'new')

    def test_04_confirm_customer_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).confirm_customer()
        self.assertEqual(self.partner.customer_state, 'confirmed')

    def test_05_approve_customer_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')

    def test_06_reject_customer_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        self.partner.sudo(self.customer_approval_user).reject_customer()
        self.assertEqual(self.partner.customer_state, 'new')

    def test_07_write_rescricted_field_with_normal_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        with self.assertRaises(WarningOdoo):
            self.partner.sudo(self.normal_user).write({
                'phone': '555-666-777',
            })
        self.assertEqual(self.partner.phone, '000-111-222')

    def test_08_write_no_rescricted_field_with_normal_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        self.partner.sudo(self.normal_user).write({
            'email': 'changedpartnertest@test.com',
        })
        self.assertEqual(self.partner.email, 'changedpartnertest@test.com')

    def test_09_write_rescricted_field_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        self.partner.sudo(self.customer_approval_user).write({
            'phone': '555-666-777'
        })
        self.assertEqual(self.partner.phone, '555-666-777')

    def test_10_write_no_rescricted_field_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        self.partner.sudo(self.customer_approval_user).write({
            'email': 'changedpartnertest@test.com',
        })
        self.assertEqual(self.partner.email, 'changedpartnertest@test.com')
