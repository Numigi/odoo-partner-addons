# © 2017-2018 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class BaseConfigSettingsWithGoogleMapsAPI(models.TransientModel):
    """Add the google maps api key to the global config settings."""

    _inherit = "res.config.settings"

    def _default_google_maps_api_key(self):
        return self.env['ir.config_parameter'].get_param('google_maps_api_key')

    def _default_google_maps_api_uri(self):
        return (
            "https://console.developers.google.com/flows/enableapi?"
            "apiid=places_backend&reusekey=true"
        )

    google_maps_api_uri = fields.Char(
        default=_default_google_maps_api_uri,
        readonly=True,
        help="The URL to generate the Google Maps Api Key")
    google_maps_api_key = fields.Char(
        default=_default_google_maps_api_key)

    @api.multi
    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param('google_maps_api_key', self.google_maps_api_key)
