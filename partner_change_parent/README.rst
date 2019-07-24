Partner Change Parent
=====================
This module adds a button in the partner form view for changing the parent entity of a contact.

Changing a parent entity is a complex operation. The contact may not be merely reassigned
to a different entity, because all documents created under the previous entity will follow
the contact under the next entity.

For example, customer invoices emited in regard to a given entity must not be reassigned to another entity.

Usage
-----
I go to the form view of a contact.

I notice that I the parent entity is readonly.

.. image:: static/description/contact_parent_readonly.png

I also notice a new button ``Change Parent Entity``.

.. image:: static/description/contact_change_parent_button.png

I click on the button. A wizard is opened, asking me to select a new parent for the contact.

.. image:: static/description/change_parent_wizard.png

I select a new parent, then I click on ``Validate``

.. image:: static/description/change_parent_wizard_validate.png

The form view of a copy of my contact is opened. This contact has the new parent entity.

.. image:: static/description/new_contact_form.png

Using the breadcrumb, I can go back to the original contact.

.. image:: static/description/new_contact_breadcrumb.png

I notice that the original contact is archived.

.. image:: static/description/old_contact_form.png

How the module works
--------------------
The following procedure is applied for changing a contact from an entity to another.

* The contact is copied.
* The copy is placed under the destination entity.
* The old contact is archived.

Portal Users
------------
If the partner is bound to an active portal user, when changing the parent entity,
a blocking message will be raised.

.. image:: static/description/portal_user_error_message.png

Before changing the parent, you must go to the form view of the portal user and archive this user.

.. image:: static/description/portal_user_archive.png

Internal Users
--------------
In the case of an internal user, the contact is not copied.
The parent entity is changed directly without creating a new partner.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Agathe Mollé (agathe.molle@savoirfairelinux.com)
* Guillaume Lot

More information
----------------
* Meet us at https://bit.ly/numigi-com
