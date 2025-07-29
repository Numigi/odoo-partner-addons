Partner Unique Email
====================
This module prevents having 2 partners with the same email.

When creating a partner with a duplicate email, it raises a clear message to the user.
This message tells the user which partner has the same email.

No SQL Constraint
-----------------
The module does not add a unique constraint to the partners.

Adding a unique constraint on an existing model usually breaks existing unit tests in other modules.
Also, it can not be installed if there are already existing duplicates in the database.

Contributors
------------

* The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.
* Yasmine El Mrini (yasmine.elmrini@savoirfairelinux.com)

