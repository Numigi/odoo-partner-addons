# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import SavepointCase
from odoo import fields
from odoo.exceptions import Warning as WarningOdoo


class TestPurchaseOrder(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()

        cls.group_purchase_manager = cls.env.ref(
            'purchase.group_purchase_manager')
        cls.group_partner_restricted_field_purchases = cls.env.ref(
            'partner_validation_purchase.group_partner_restricted_field_purchases')

        cls.normal_user = cls.env['res.users'].create({
            'name': 'Normal User',
            'login': 'normaluserlogin',
            'email': 'normaluser@test.com',
            'groups_id': [(6, 0, [
                cls.group_purchase_manager.id,
            ])],
        })

        cls.supplier_approval_user = cls.env['res.users'].create({
            'name': 'Controller Approval User',
            'login': 'controllerapprovaluserlogin',
            'email': 'controllerapprovaluser@test.com',
            'groups_id': [(6, 0, [
                cls.group_purchase_manager.id,
                cls.group_partner_restricted_field_purchases.id,
            ])],
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner Test',
            'is_company': True,
            'phone': '000-111-222',
            'email': 'partnertest@test.com',
            'supplier': True,
            'supplier_state': 'new'
        })

        cls.purchase_order = cls._create_purchase_order(cls, cls.partner)

    def test_01_confirm_purchase_of_new_partner_with_normal_user(self):
        with self.assertRaises(WarningOdoo):
            self.purchase_order.sudo(self.normal_user).button_confirm()
        self.assertEqual(self.purchase_order.state, 'draft')

    def test_02_confirm_purchase_of_new_partner_with_approval_user(self):
        with self.assertRaises(WarningOdoo):
            self.purchase_order.sudo(self.supplier_approval_user).button_confirm()
        self.assertEqual(self.purchase_order.state, 'draft')

    def test_03_confirm_purchase_of_confirmed_partner_with_normal_user(self):
        self.partner.sudo(self.supplier_approval_user).confirm_supplier()
        self.assertEqual(self.partner.supplier_state, 'confirmed')
        with self.assertRaises(WarningOdoo):
            self.purchase_order.sudo(self.normal_user).button_confirm()
        self.assertEqual(self.purchase_order.state, 'draft')

    def test_04_confirm_purchase_of_confirmed_partner_with_approval_user(self):
        self.partner.sudo(self.supplier_approval_user).confirm_supplier()
        self.assertEqual(self.partner.supplier_state, 'confirmed')
        with self.assertRaises(WarningOdoo):
            self.purchase_order.sudo(self.supplier_approval_user).button_confirm()
        self.assertEqual(self.purchase_order.state, 'draft')

    def test_05_confirm_purchase_of_approved_partner_with_normal_user(self):
        self.partner.sudo(self.supplier_approval_user).approve_supplier()
        self.assertEqual(self.partner.supplier_state, 'approved')
        self.purchase_order.sudo(self.normal_user).button_confirm()
        self.assertEqual(self.purchase_order.state, 'purchase')

    def test_06_confirm_purchase_of_approved_partner_with_approval_user(self):
        self.partner.sudo(self.supplier_approval_user).approve_supplier()
        self.assertEqual(self.partner.supplier_state, 'approved')
        self.purchase_order.sudo(self.supplier_approval_user).button_confirm()
        self.assertEqual(self.purchase_order.state, 'purchase')

    def _create_purchase_order(self, partner):
        purchase_obj = self.env['purchase.order']
        product_values = {'name': 'Test product',
                          'list_price': 5,
                          'type': 'product'}
        product = self.env['product.product'].create(product_values)
        product_uom_unit = self.env.ref('product.product_uom_unit')
        now = fields.Datetime.now()
        values = {
            'partner_id': partner.id,
            'date_planned': now,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom': product_uom_unit.id,
                'price_unit': product.list_price,
                'product_qty': 1,
                'date_planned': now
            })],
        }
        return purchase_obj.create(values)
