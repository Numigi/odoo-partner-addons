# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models
from lxml import etree
from ..utils.orm import setup_modifiers


class ResPartnerAutocompleteDisable(models.Model):
    _inherit = "res.partner"

    @api.model
    def _rpc_remote_api(self, *args, **kwargs):
        return {}, False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(ResPartnerAutocompleteDisable, self).fields_view_get(view_id=view_id,
            view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='name']"):
                if node.get("widget") == 'field_partner_autocomplete':
                    node.set('widget', '')
                    setup_modifiers(node, res['fields']['name'])
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
