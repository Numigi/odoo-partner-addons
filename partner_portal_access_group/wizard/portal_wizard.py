# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import AccessError


class PortalWizard(models.TransientModel):

    _inherit = "portal.wizard"

    def action_apply(self):
        has_access = self.env.user.has_group("partner_portal_access_group.group_portal_access")

        if not has_access:
            raise AccessError(
                _(
                    "Only members of the group `Manage Portal Access` are allowed "
                    "to invite partners to the portal."
                )
            )

        super(PortalWizard, self.sudo()).action_apply()
