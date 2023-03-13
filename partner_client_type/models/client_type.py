# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ClientType(models.Model):
    _name = "client.type"
    _description = "Client Type"
    _order = "name"

    name = fields.Text(translate=True)
    active = fields.Boolean(default=True)
