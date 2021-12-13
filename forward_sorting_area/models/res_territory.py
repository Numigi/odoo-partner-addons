# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResTerritory(models.Model):

    _name = "res.territory"
    _description = "Territory"
    _inherit = "mail.thread"

    name = fields.Char(
        "Name",
        required=True,
        track_visibility="onchange",
    )

    fsa_ids = fields.Many2many(
        "forward.sortation.area",
        "res_territory_fsa_rel",
        "territory_id",
        "fsa_id",
        string="FSA",
        track_visibility="onchange",
    )

    partner_ids = fields.Many2many(
        string="Partners", comodel_name="res.partner", relation="rel_territory_partner"
    )

    color = fields.Integer(
        "Color Index",
        track_visibility="onchange",
    )
    active = fields.Boolean(
        "Active",
        default=True,
        track_visibility="onchange",
    )
