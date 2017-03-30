# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models

tracked_fields = {
    'name', 'date', 'title', 'parent_id', 'parent_name', 'ref', 'lang',
    'tz', 'user_id', 'vat', 'website', 'comment', 'credit_limit', 'ean13',
    'active', 'customer', 'supplier', 'employee', 'function', 'type',
    'street', 'street2', 'zip', 'city', 'state_id', 'country_id', 'email',
    'phone', 'fax', 'mobile', 'birthdate', 'is_company', 'use_parent_address',
    'has_image', 'company_id', 'color', 'vat_subjected', 'debit_limit',
    'property_account_receivable', 'property_account_position',
    'property_payment_term', 'property_supplier_payment_term',
    'last_reconciliation_date'
}


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

    # fields defined in 'base' module
    name = fields.Char(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    title = fields.Many2one(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    parent_name = fields.Char(track_visibility='onchange')
    ref = fields.Char(track_visibility='onchange')
    lang = fields.Selection(track_visibility='onchange')
    tz = fields.Selection(track_visibility='onchange')
    user_id = fields.Many2one(track_visibility='onchange')
    vat = fields.Char(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')
    comment = fields.Text(track_visibility='onchange')
    credit_limit = fields.Float(track_visibility='onchange')
    ean13 = fields.Char(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    customer = fields.Boolean(track_visibility='onchange')
    supplier = fields.Boolean(track_visibility='onchange')
    employee = fields.Boolean(track_visibility='onchange')
    function = fields.Char(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    fax = fields.Char(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')
    birthdate = fields.Char(track_visibility='onchange')
    is_company = fields.Boolean(track_visibility='onchange')
    use_parent_address = fields.Boolean(track_visibility='onchange')
    has_image = fields.Boolean(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    color = fields.Integer(track_visibility='onchange')

    # fields defined in 'account' module
    vat_subjected = fields.Boolean(track_visibility='onchange')
    debit_limit = fields.Float(track_visibility='onchange')
    property_account_receivable = fields.Many2one(track_visibility='onchange')
    property_account_position = fields.Many2one(track_visibility='onchange')
    property_payment_term = fields.Many2one(track_visibility='onchange')
    property_supplier_payment_term = fields.Many2one(
        track_visibility='onchange'
    )
    last_reconciliation_date = fields.Datetime(track_visibility='onchange')

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
        if self.env.context.get('params'):
            user_preferences_action = self.env.ref('base.action_res_users_my')
            if (
                self.env.context.get('params').get('action') ==
                user_preferences_action.id
            ):  # write() is called from the user changing his preferences
                return super(ResPartner, self).write(vals)
        user = self.env['res.users'].browse(self.env.uid)
        if not user.has_group('partner_tracking.group_partner_validation'):
            for rec in self:
                if rec.state == 'controlled':
                    tracked_vals = [field for field in vals if (
                        field in tracked_fields
                    )]
                    if any(rec[field] != vals[field] for field in
                           tracked_vals):
                        vals['state'] = 'pending'
        return super(ResPartner, self).write(vals)
