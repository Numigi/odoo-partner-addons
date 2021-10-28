Partner Key Dates
=================
This module adds key dates on partners.

A key date is an important event in the timeline of a contact.



Configuration
-------------------

Multiple date types can be configured under the menu Contacts / Configuration / Key Date Types.

.. image:: static/description/odoo_partner_key_dates_00.png

These types will be available in the key date section on the partner.

On the Key Date Type, it is possible to set an email template that will be sent on the date anniversary.

.. image:: static/description/odoo_partner_key_dates_key_date_mail_template.png

A "Send Partner Anniversary Email" is available by default with the module.

.. image:: static/description/odoo_partner_key_dates_email_template.png



Usage
-------------------

Key dates can be accessed from Contacts / Dates.

.. image:: static/description/odoo_partner_key_dates_01.png

The colomn "Age" is automatically computed from the key Date. The computation is done when saving the form view.

.. image:: static/description/odoo+partner_key_dates_age.png

...or with a daily cron.

.. image:: static/description/odoo_partner_key_dates_compute_cron.png

The column "Diffusion" allows to check dates for which an email
must be sent at the anniversary of a key date.

.. image:: static/description/odoo_partner_key_dates_edit.png


Anniversary Emails
------------------
The modules adds a cron to send an email on the anniversary of a key date.

.. image:: static/description/odoo_partner_key_dates_send_email_cron.png

At anniversary, if the "Diffusion" option is activated on the date, an email is sent.

.. image:: static/description/odoo_partner_key_dates_email_sent.png


Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Savoir-faire linux

More information
----------------
* Meet us at https://bit.ly/numigi-com
