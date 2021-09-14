# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ClientType(models.Model):
    _name = "client.type"
    _description = "Client Type"

    name = fields.Text()
    active = fields.Boolean()
