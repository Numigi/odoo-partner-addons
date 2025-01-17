Partner Phone No Envelope
=========================

In Odoo, since version 11.0, an envelope appears beside the phone numbers on partner forms.
The envelope only works if an In-App Purchase (IAP) account is enabled.

.. image:: static/description/before_install.png?raw=true
   :alt: Before Installing

This module hides the envelope, in case you do a mouse-over on the phone number, or click on it to edit.

.. image:: static/description/after_install.png?raw=true
   :alt: After Installing

Displaying The Envelopes
------------------------

The envelope is hidden based on a system parameter ``partner_phone_no_envelope.hide_envelope``
which defaults to True, and if values on parameter is not `False` or `0`.

To render the envelope visible:

* Go to **Configuration / Technical / Parameters / System Parameters**.
* Add a new parameter called ``partner_phone_no_envelope.hide_envelope``.
* Set the value of ``partner_phone_no_envelope.hide_envelope`` to False.

Contributors
------------

* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
-----------------

* Meet us at https://bit.ly/numigi-com
