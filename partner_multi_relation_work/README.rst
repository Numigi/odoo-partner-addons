Partner Multi Relation Work
===========================
This module adds employer/employee relationships.

When a contact is created, a relation with the parent entity is automatically added.

Changing the parent of a contact
--------------------------------
When a contact moves from a company to another (see module partner_change_parent),
new relations are added between the involved partners.

* A relation is created between the archived contact and the new one saying that the 2 contacts are the same person.
* A work relation is created between the new contact and the previous entity.
* A work relation is created between the new contact and the destination entity.
* All other relations from the archived contact are copied to the new one.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Agathe Mollé (agathe.molle@savoirfairelinux.com)
* Guillaume Lot

More information
----------------
* Meet us at https://bit.ly/numigi-com
