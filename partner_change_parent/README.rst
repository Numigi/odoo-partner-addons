Partner Change Parent
=====================
This module adds a button in the partner form view for changing the parent entity of a contact.

Changing a parent entity is a complex operation. The contact may not be merely reassigned
to a different entity, because all documents created under the previous entity will follow
the contact under the next entity.

For example, customer invoices emited in regard to a given entity must not be reassigned to another entity.

How the module works
--------------------
The following procedure is applied for changing a contact from an entity to another.

* The contact is copied.
* The copy is placed under the destination entity.
* The old contact is archived.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Agathe Mollé (agathe.molle@savoirfairelinux.com)
* Guillaume Lot

More information
----------------
* Meet us at https://bit.ly/numigi-com
