from odoo import api, models


class Contact(models.Model):
    """This class was copied from the module crm_phone_validation.

    The original code can be found here:
    https://github.com/odoo/odoo/blob/12.0/addons/crm_phone_validation/models/res_partner.py
    """

    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']

    @api.onchange('phone', 'country_id', 'company_id')
    def _onchange_phone_validation(self):
        if self.phone:
            self.phone = self.phone_format(self.phone)

    @api.onchange('mobile', 'country_id', 'company_id')
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self.phone_format(self.mobile)
