Partner Affiliate Invoicing Address
===================================

.. contents:: Table of Contents

Context
-------
The module `partner_affiliate <https://github.com/OCA/partner-contact/tree/12.0/partner_affiliate>`_
allows to define child commercial partners (affiliates) under a common parent entity.

.. image:: static/description/partner_affiliates.png

By default, the invoicing address of each affiliate is used when selling to an affiliate.

Therefore, defining an invoicing address on the parent entity
has no impact on invoices of its affiliates.

.. image:: static/description/order_with_affiliate_invoice_address.png

Usage
-----
This module adds a checkbox ``Use Parent Invoice Address``.

.. image:: static/description/partner_checkbox.png

When this box is checked, the invoicing address for this affiliate will be
selected from its parent entity.

.. image:: static/description/order_with_parent_invoice_address.png

Configurations and functionalities since version 1.0.1
------------------------------------------------------
As an internal user, I go to the form view of an `Affiliate`` (``Company`` type contact, child of a ``Company`` type contact).

From the ``Contacts & Addresses`` tab,
- I click on ``Use parent Invoice address``.
- I see that a new required field ``Invoice Address to use`` is displayed. 
The parent's billing address (vanilla behavior of the module) is entered as the default value.

.. image:: static/description/default_address_used.png

I see that I can select:
- another invoice address of the parent company (Address Type = Invoice Address) 
- the main address of the parent company

.. image:: static/description/more_choices_on_invoice_address.png

As a Sales user, I create a sales order for customer ``Azure Montreal`` or one of its children.

I see that the invoice address selected is the invoice address defined previously.

.. image:: static/description/sale_invoice_address.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
