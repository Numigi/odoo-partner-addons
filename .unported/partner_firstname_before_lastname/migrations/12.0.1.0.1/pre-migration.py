# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def set_partner_names_order_in_res_config_settings(cr):
    """Set the value partner_names_order in res_config_settings.

    This prevents the following SQL error on every module update.
    psycopg2.IntegrityError: column "partner_names_order" contains null values
    """
    cr.execute("UPDATE res_config_settings SET partner_names_order = 'first_last';")


def migrate(cr, version):
    set_partner_names_order_in_res_config_settings(cr)
