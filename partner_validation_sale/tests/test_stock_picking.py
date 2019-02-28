# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import SavepointCase
from odoo.exceptions import Warning as WarningOdoo


class TestSaleOrder(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()

        cls.group_stock_manager = cls.env.ref(
            'stock.group_stock_manager')
        cls.group_partner_restricted_field_sales = cls.env.ref(
            'partner_validation_sale.group_partner_restricted_field_sales')

        cls.normal_user = cls.env['res.users'].create({
            'name': 'Normal User',
            'login': 'normaluserlogin',
            'email': 'normaluser@test.com',
            'groups_id': [(6, 0, [
                cls.group_stock_manager.id,
            ])],
        })

        cls.customer_approval_user = cls.env['res.users'].create({
            'name': 'Controller Approval User',
            'login': 'controllerapprovaluserlogin',
            'email': 'controllerapprovaluser@test.com',
            'groups_id': [(6, 0, [
                cls.group_stock_manager.id,
                cls.group_partner_restricted_field_sales.id,
            ])],
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner Test',
            'is_company': True,
            'customer': True,
            'customer_state': 'new'
        })

        cls.outgoing_picking = cls._create_picking(cls.partner, 'outgoing')
        cls.internal_picking = cls._create_picking(cls.partner, 'internal')
        cls.incoming_picking = cls._create_picking(cls.partner, 'incoming')

    @classmethod
    def _create_picking(cls, partner, picking_type='outgoing'):
        if picking_type == 'internal':
            src_location = cls.env.ref('stock.stock_location_stock')
            dest_location = cls.env.ref('stock.stock_location_stock')
            p_type = cls.env.ref('stock.picking_type_internal')

        elif picking_type == 'incoming':
            src_location = cls.env.ref('stock.stock_location_suppliers')
            dest_location = cls.env.ref('stock.stock_location_stock')
            p_type = cls.env.ref('stock.picking_type_in')

        elif picking_type == 'purchase_return':
            src_location = cls.env.ref('stock.stock_location_stock')
            dest_location = cls.env.ref('stock.stock_location_suppliers')
            p_type = cls.env.ref('stock.picking_type_out')

        else:
            src_location = cls.env.ref('stock.stock_location_stock')
            dest_location = cls.env.ref('stock.stock_location_customers')
            p_type = cls.env.ref('stock.picking_type_out')

        picking = cls.env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': p_type.id,
            'location_id': src_location.id,
            'location_dest_id': dest_location.id,
        })

        product_values = {'name': 'Test product',
                          'list_price': 5,
                          'type': 'product'}
        product = cls.env['product.product'].create(product_values)

        cls.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom_qty': 1,
            'quantity_done': 1,
            'product_uom': product.uom_id.id,
            'location_id': src_location.id,
            'location_dest_id': dest_location.id,
        })
        picking.action_confirm()
        picking.force_assign()
        return picking

    def test_01_validate_outgoing_picking_of_new_partner_with_normal_user(self):
        with self.assertRaises(WarningOdoo):
            self.outgoing_picking.sudo(self.normal_user).button_validate()

    def test_02_validate_outgoing_picking_of_new_partner_with_approval_user(self):
        with self.assertRaises(WarningOdoo):
            self.outgoing_picking.sudo(self.customer_approval_user).button_validate()

    def test_03_validate_outgoing_picking_of_confirmed_partner_with_normal_user(self):
        self.partner.sudo(self.customer_approval_user).confirm_customer()
        self.assertEqual(self.partner.customer_state, 'confirmed')
        with self.assertRaises(WarningOdoo):
            self.outgoing_picking.sudo(self.normal_user).button_validate()

    def test_04_validate_outgoing_picking_of_confirmed_partner_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).confirm_customer()
        self.assertEqual(self.partner.customer_state, 'confirmed')
        with self.assertRaises(WarningOdoo):
            self.outgoing_picking.sudo(self.customer_approval_user).button_validate()

    def test_05_validate_outgoing_picking_of_approved_partner_with_normal_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        res = self.outgoing_picking.sudo(self.normal_user).button_validate()
        self.assertIsNone(res)

    def test_06_validate_outgoing_picking_of_approved_partner_with_approval_user(self):
        self.partner.sudo(self.customer_approval_user).approve_customer()
        self.assertEqual(self.partner.customer_state, 'approved')
        res = self.outgoing_picking.sudo(self.customer_approval_user).button_validate()
        self.assertIsNone(res)

    def test_07_validate_internal_picking_of_new_partner_with_normal_user(self):
        self.assertEqual(self.partner.customer_state, 'new')
        res = self.internal_picking.sudo(self.normal_user).button_validate()
        self.assertIsNone(res)

    def test_08_validate_internal_picking_of_new_partner_with_approval_user(self):
        self.assertEqual(self.partner.customer_state, 'new')
        res = self.internal_picking.sudo(self.customer_approval_user).button_validate()
        self.assertIsNone(res)

    def test_09_validate_incoming_picking_of_new_partner_with_normal_user(self):
        self.assertEqual(self.partner.customer_state, 'new')
        res = self.incoming_picking.sudo(self.normal_user).button_validate()
        self.assertIsNone(res)

    def test_10_validate_incoming_picking_of_new_partner_with_approval_user(self):
        self.assertEqual(self.partner.customer_state, 'new')
        res = self.incoming_picking.sudo(self.customer_approval_user).button_validate()
        self.assertIsNone(res)

    def test_on_purchase_return__constraints_are_not_triggered(self):
        return_picking = self._create_picking(self.partner, 'purchase_return')
        self.assertEqual(self.partner.customer_state, 'new')
        res = return_picking.sudo(self.normal_user).button_validate()
        self.assertIsNone(res)
