Partner Validation Sale
=======================
This module add contrainsts on Contacts / Sale Orders / Stock Pickings (outgoing).

Customer Approval Group
~~~~~~~~~~~~~~~~~~~~~~~
A new group `Customer Approval` is added.

.. image:: static/description/customer_approval_group.png

This group allows to approve a partner as a customer.

Customer State
--------------
In the form view of a partner, a new field `Customer State` is added.

.. image:: static/description/partner_form.png

This field has 3 values:

* New
* Confirmed
* Approved

It is only visible if the partner is a customer.
It is only visible on a commercial partner (i.e. it is not visible on a contact or a billing address).

Confirm
~~~~~~~
The `Confirm` button changes the customer state to `Confirmed`.

.. image:: static/description/partner_form_confirm_button.png

.. image:: static/description/partner_form_confirmed.png

Any user with write access to the partner can click on the button.

Approve
~~~~~~~
The `Approve` button changes the customer state to `Approved`.

.. image:: static/description/partner_form_approve_button.png

.. image:: static/description/partner_form_approved.png

Only members of the group `Customer Approval` can click on the button.
The button is invisible for other users.

Reject
~~~~~~
The `Reject` button changes the customer state to `New`.

.. image:: static/description/partner_form_reject_button.png

.. image:: static/description/partner_form_new.png

Any user with write access to the partner can click on the button.

Sale Order Confirmation
-----------------------
When confirming a quotation, if the commercial partner related to the customer is not approved
as a customer, a blocking message is shown to the user.

.. image:: static/description/quotation_form.png

.. image:: static/description/quotation_form_error_message.png

The customer must be approved by a member of the `Customer Approval` Group before
confirming the sale order.

Delivery Validation
-------------------
When validating a delivery order, if the commercial partner related to the customer is not approved
as a customer, a blocking message is shown to the user.

.. image:: static/description/delivery_form.png

.. image:: static/description/delivery_form_error_message.png

The customer must be approved by a member of the `Customer Approval` Group before
validating the delivery order.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Akretion

More information
----------------
* Meet us at https://bit.ly/numigi-com
