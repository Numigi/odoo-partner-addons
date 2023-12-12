# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

CUSTOM_CATEGORY_FIELDS = (
    'organization_type_ids',
    'profile_ids',
    'personality_ids',
    'job_position_id',
)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    organization_type_ids = fields.Many2many(
        'res.partner.category', 'res_partner_category_organization_type_rel',
        'partner_id', 'organization_type_id',
        domain=[('type', '=', 'organization_type')],
        string='Organization Type')
    profile_ids = fields.Many2many(
        'res.partner.category', 'res_partner_category_profile_rel',
        'partner_id', 'profile_id',
        domain=[('type', '=', 'profile')],
        string='Profile')
    personality_ids = fields.Many2many(
        'res.partner.category', 'res_partner_category_personality_rel',
        'partner_id', 'personality_id',
        domain=[('type', '=', 'personality')],
        string='Personality')
    job_position_id = fields.Many2one(
        'res.partner.category', domain=[('type', '=', 'job_position')],
        string='Job Position')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._update_category_ids_from_extra_caetgory_fields()
        return res

    @api.multi
    def write(self, vals):
        super().write(vals)
        if any(f in vals for f in CUSTOM_CATEGORY_FIELDS):
            for partner in self:
                partner._update_category_ids_from_extra_caetgory_fields()
        return True

    def _update_category_ids_from_extra_caetgory_fields(self):
        """Update the partner tags from the custom category fields."""
        new_categories = (
                self.organization_type_ids |
                self.profile_ids |
                self.personality_ids |
                self.job_position_id
        )
        if new_categories != self.category_id:
            self.category_id = new_categories

    def cron_fill_contact_tags(self):
        """
        Fill empty contact tags using the category_id
        :return:
        """
        domain = [
            ('organization_type_ids', '=', False),
            ('profile_ids', '=', False),
            ('personality_ids', '=', False),
            ('job_position_id', '=', False),
            ('category_id', '!=', False),
                  ]
        partner_ids = self.sudo().search(domain)
        for partner in partner_ids:
            for categ_id in partner.category_id:
                if categ_id.type == 'organization_type':
                    partner.organization_type_ids = [(4, categ_id.id)]
                if categ_id.type == 'profile':
                    partner.profile_ids = [(4, categ_id.id)]
                if categ_id.type == 'personality':
                    partner.personality_ids = [(4, categ_id.id)]
                if categ_id.type == 'job_position':
                    partner.job_position_id = categ_id.id
