# © 2017-2018 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartnerWithPlace(models.Model):
    """Add a field place on the partners.

    The field does not need to be stored as a column.

    However, it needs to be defined in order to be placed inside the form view.

    The place widget must be defined as a field in the form view because
    otherwise, when pressing `TAB` in the web interface, the autocomplete input
    is bypassed.
    """

    _inherit = 'res.partner'

    # The compute parameter prevents adding a column in the res_partner table.
    # The inverse parameter makes the field editable in views.
    place = fields.Char(compute=lambda self: None, inverse=lambda self: None)
