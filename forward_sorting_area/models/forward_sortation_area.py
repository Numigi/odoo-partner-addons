# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ForwardSortationAera(models.Model):

    _name = "forward.sortation.area"
    _description = "Forward Sorting Area"
    _inherit = "mail.thread"

    name = fields.Char(
        "Name",
        required=True,
        track_visibility="onchange",
    )
    sector = fields.Char(
        "Sector",
        track_visibility="onchange",
    )
    province = fields.Char(
        "Province",
        track_visibility="onchange",
    )
    latitude = fields.Char(
        "Latitude",
        track_visibility="onchange",
    )
    longitude = fields.Char(
        "Longitude",
        track_visibility="onchange",
    )
    active = fields.Boolean(
        "Active",
        default=True,
        track_visibility="onchange",
    )

    territory_ids = fields.Many2many(
        "res.territory",
        "res_territory_fsa_rel",
        "fsa_id",
        "territory_id",
        string="Territories",
        track_visibility="onchange",
    )

    partner_ids = fields.One2many("res.partner", "fsa_id", string="Partners")

    @api.multi
    def write(self, vals):
        res = super(ForwardSortationAera, self).write(vals)
        if "name" in vals:
            self.mapped("partner_ids")._compute_fsa_id()
            self.env["res.partner"].search(
                [
                    ("zip", "ilike", vals["name"] + "%"),
                ]
            )._compute_fsa_id()

        return res
