# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.exceptions import Warning

TRACKED_FIELDS = {
    'name', 'date', 'title', 'parent_id', 'ref', 'lang',
    'tz', 'user_id', 'vat', 'website', 'comment', 'credit_limit', 'ean13',
    'active', 'customer', 'supplier', 'employee', 'function', 'type',
    'street', 'street2', 'zip', 'city', 'state_id', 'country_id', 'email',
    'phone', 'fax', 'mobile', 'birthdate', 'is_company', 'use_parent_address',
    'has_image', 'company_id', 'color', 'vat_subjected', 'debit_limit',
    'property_account_payable',
    'property_account_receivable', 'property_account_position',
    'property_payment_term', 'property_supplier_payment_term',
}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection(
        string='Status',
        selection=[
            ('pending', 'To Validate'),
            ('controlled', 'Controlled'),
        ],
        readonly=True,
        track_visibility='onchange',
    )

    tracking_write_date = fields.Datetime(
        string='Last Updated on',
        readonly=True
    )

    tracking_write_uid = fields.Many2one(
        string='Last Updated by',
        comodel_name='res.users',
        readonly=True
    )

    # fields defined in 'base' module
    name = fields.Char(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    title = fields.Many2one(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
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
    company_id = fields.Many2one(track_visibility='onchange')

    # fields defined in 'account' module
    vat_subjected = fields.Boolean(track_visibility='onchange')
    debit_limit = fields.Float(track_visibility='onchange')
    property_account_payable = fields.Many2one(track_visibility='onchange')
    property_account_receivable = fields.Many2one(track_visibility='onchange')
    property_account_position = fields.Many2one(track_visibility='onchange')
    property_payment_term = fields.Many2one(track_visibility='onchange')
    property_supplier_payment_term = fields.Many2one(
        track_visibility='onchange'
    )

    @api.model
    def get_tracked_fields(self):
        return set(TRACKED_FIELDS)

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        user = self.env.user
        if user.has_group('partner_tracking.group_partner_validation'):
            partner.sudo().state = 'controlled'
        else:
            partner.sudo().state = 'pending'
        partner.tracking_write_date = fields.Datetime.now()
        partner.tracking_write_uid = self.env.user.id
        return partner

    @api.multi
    def write(self, vals):
        """
        Change state to 'pending' if values have been updated by a user that
        is not part of the validation group
        """
        user = self.env.user
        if 'state' in vals and not user.has_group(
            'partner_tracking.group_partner_validation'
        ):
            raise Warning(_(
                "Permission to change the state of the partner denied."
            ))
        if user.id != SUPERUSER_ID or 'state' in vals:
            vals['tracking_write_date'] = fields.Datetime.now()
            vals['tracking_write_uid'] = user.id

        standard_partners = self.filtered(lambda p: not p.user_ids)

        if not user.has_group('partner_tracking.group_partner_validation'):
            tracked_fields = self.get_tracked_fields()
            for rec in standard_partners:
                if rec.state == 'controlled':
                    tracked_vals = [field for field in vals if (
                        field in tracked_fields
                    )]
                    if any(rec[field] != vals[field] for field in
                           tracked_vals):
                        vals['state'] = 'pending'

        return super(ResPartner, self).write(vals)
