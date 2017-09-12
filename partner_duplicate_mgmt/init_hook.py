# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def update_partners_indexed_name(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    logger.info('Updating indexed name for all partners')
    partners = env['res.partner'].search([])
    partners._update_indexed_name()
