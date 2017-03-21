# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection(
        string='Status',
        selection=[
            ('pending', 'To Validate'),
            ('controlled', 'Controlled'),
        ],
        default='controlled',
        readonly=True,
    )

    name = fields.Char(track_visibility='onchange')
    is_company = fields.Boolean(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange')
    tz = fields.Many2one(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')
    fax = fields.Char(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    title = fields.Many2one(track_visibility='onchange')
    comment = fields.Text(track_visibility='onchange')
    user_id = fields.Many2one(track_visibility='onchange')
    section_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    customer = fields.Boolean(track_visibility='onchange')
    supplier = fields.Boolean(track_visibility='onchange')
    employee = fields.Boolean(track_visibility='onchange')
    is_employee_contact = fields.Boolean(track_visibility='onchange')
    is_employee_address = fields.Boolean(track_visibility='onchange')
    ref = fields.Char(track_visibility='onchange')
    lang = fields.Selection(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    website_published = fields.Boolean(track_visibility='onchange')
    opt_out = fields.Boolean(track_visibility='onchange')
    property_product_pricelist = fields.Many2one(track_visibility='onchange')
    property_product_pricelist_purchase = fields.Many2one(
        track_visibility='onchange'
    )
    property_stock_customer = fields.Many2one(track_visibility='onchange')
    property_stock_supplier = fields.Many2one(track_visibility='onchange')
    payment_responsible_id = fields.Many2one(track_visibility='onchange')
    payment_next_action = fields.Text(track_visibility='onchange')
    payment_note = fields.Text(track_visibility='onchange')
    property_account_position = fields.Many2one(track_visibility='onchange')
    vat = fields.Char(track_visibility='onchange')
    vat_subjected = fields.Boolean(track_visibility='onchange')
    property_account_receivable = fields.Many2one(track_visibility='onchange')
    property_payment_term = fields.Many2one(track_visibility='onchange')
    credit_limit = fields.Float(track_visibility='onchange')
    debit_limit = fields.Float(track_visibility='onchange')
    last_reconciliation_date = fields.Datetime(track_visibility='onchange')
    property_account_payable = fields.Many2one(track_visibility='onchange')
    property_supplier_payment_term = fields.Many2one(
        track_visibility='onchange'
    )
    function = fields.Char(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    use_parent_address = fields.Boolean(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    ean13 = fields.Char(track_visibility='onchange')

    @api.multi
    def action_set_controlled(self):
        """
        Change the state to 'controlled'.
        """
        for rec in self:
            rec.state = 'controlled'

    @api.multi
    def write(self, vals):
        """
        Change state to 'pending' if values have been updated by a user that
        is not part of the validation group
        """
        user = self.env['res.users'].browse(self.env.uid)
        if not user.has_group('partner_tracking.group_partner_validation'):
            for rec in self:
                if rec.state == 'controlled':
                    for field in vals:
                        if rec[field] != vals[field]:
                            vals['state'] = 'pending'
                            break
        return super(ResPartner, self).write(vals)
