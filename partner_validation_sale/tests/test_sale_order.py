# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import SavepointCase
from odoo.exceptions import Warning as WarningOdoo


class TestSaleOrder(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()

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
            'customer': True,
            'customer_state': 'new'
        })

        cls.sale_order = cls._create_sale_order(cls, cls.partner)

    def test_01_confirm_sale_of_new_partner_with_normal_user(self):
        with self.assertRaises(WarningOdoo):
            self.sale_order.sudo(self.normal_user).action_confirm()
        self.assertEqual(self.sale_order.state, 'draft')

    def test_02_confirm_sale_of_new_partner_with_approval_user(self):
        with self.assertRaises(WarningOdoo):
            self.sale_order.sudo(self.customer_approval_user).action_confirm()
        self.assertEqual(self.sale_order.state, 'draft')

    def test_03_confirm_sale_of_confirmed_partner_with_normal_user(self):
        self.partner.sudo(self.customer_approval_user).confirm_customer()
        self.assertEqual(self.partner.customer_state, 'confirmed')
        with self.assertRaises(WarningOdoo):
            self.sale_order.sudo(self.normal_user).action_confirm()
        self.assertEqual(self.sale_order.state, 'draft')

    def test_04_confirm_sale_of_confirmed_partner_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).confirm_customer()
        self.assertEqual(self.partner.customer_state, 'confirmed')
        with self.assertRaises(WarningOdoo):
            self.sale_order.sudo(self.customer_approval_user).action_confirm()
        self.assertEqual(self.sale_order.state, 'draft')

    def test_05_confirm_sale_of_approved_partner_with_normal_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        self.sale_order.sudo(self.normal_user).action_confirm()
        self.assertEqual(self.sale_order.state, 'sale')

    def test_06_confirm_sale_of_approved_partner_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        self.sale_order.sudo(self.customer_approval_user).action_confirm()
        self.assertEqual(self.sale_order.state, 'sale')

    def _create_sale_order(self, partner):
        sale_obj = self.env['sale.order']
        product_values = {'name': 'Test product',
                          'list_price': 5,
                          'type': 'product'}
        product = self.env['product.product'].create(product_values)
        product_uom_unit = self.env.ref('product.product_uom_unit')
        values = {
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom': product_uom_unit.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1})],
        }
        return sale_obj.create(values)
