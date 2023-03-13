# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    logger.info('Updating partner full text index')
    partners = env['res.partner'].with_context(active_test=False).search([])
    partners.update_full_text()
