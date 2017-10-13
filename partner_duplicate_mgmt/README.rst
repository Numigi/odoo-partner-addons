Partner Duplicate Mgmt
======================
This module improves the user experience for managing duplicate partners.


Finding duplicate partners
--------------------------
When a partner is created or his name changes, the system will automatically search partners with similar names.

A smart button 'Duplicates' in the partner form view will appear if any potential duplicate is found.
If you click on the button, the list of duplicates will appear.

This list contains 3 columns

+---+---------------------------+------------------------------+-------------+
+   | Partner 1                 | Partner 2                    | State       |
+===+===========================+==============================+=============+
+[ ]| Michelle Fletcher         | Agrolait, Michel Fletcher    | To Validate |
+---+---------------------------+------------------------------+-------------+

Then, you may select your duplicate row and click on Action -> Merge Partners.

A wizard will appear, asking you which partner you would like to keep.
Then, you may select the field values to keep from each partner.


Partner Preserved:  Agrolait, Michel Fletcher

Partner 1:          Michelle Fletcher          Partner 2:         Agrolait, Michel Fletcher

+---------------+---------------------------+----------+------------------------------+----------+
+ Field         | Partner 1 Value           | Selected | Partner 2 Value              | Selected |
+===============+===========================+==========+==============================+==========+
+ Name          | Michelle Fletcher         | [x]      | Michel Fletcher              | [ ]      |
+---------------+---------------------------+----------+------------------------------+----------+
+ Postal Code   | G1G 3J9                   | [x]      | G1G 3J9                      | [ ]      |
+---------------+---------------------------+----------+------------------------------+----------+
+ Parent        |                           | [ ]      | Agrolait                     | [x]      |
+---------------+---------------------------+----------+------------------------------+----------+


Then, you must click on the button Merge Partners. The behavior will be the following:

* The system will merge the origin partner into the preserved partner.
* The values of the preserved partner will be updated.
* User's actions are registred in the chatter
* The source partner will be set to inactive (instead of deleted).


A new list view shows alls duplicates. The user can:

* merge (like previous step),
* exclude the duplicate by choice 


Adjusting the list of fields
----------------------------
The list of fields that appear in the merge wizard is configurable from the menu
Contacts -> Duplicate Management -> Partner Duplicate Fields.


Adjusting the similarity level
------------------------------
The similarity is computed using a trigram index.
The level of similarity required so that 2 partners are considered duplicates is 0.7 by default.
This may be changed in system parameters.


Element comparison
----------------
In the actual version, we setted by choice the comparison only on the name of res.partner
No matter what is the value in boolean 'is a company'


Adding terms to exclude from the name comparison
------------------------------------------------
When comparing 2 partners, some terms must be excluded from the names.
Such terms include Inc. If you have 2 partners Agrolait and Agrolait Inc, the similarity should be 100%.

The list of terms to exclude is configurable from the menu
Contacts -> Duplicate Management -> Partner Duplicate Terms.


Contributors
------------
* Yasmine El Mrini (yasmine.elmrini@savoirfairelinux.com)
* David Dufresne (david.dufresne@savoirfairelinux.com)
* Bruno Joliveau (bruno.joliveau@savoirfairelinux.com)


Dependencies
------------
The module uses trigrams to compare names of partners. The postgresql extension pg_trgm is required for this purpose.
If your Odoo user is not superuser on the database (which is mostlikely the case in production), the module might
not install properly.

In order to install the extension, you may log in to your database as superuser and run:

> CREATE EXTENSION pg_trgm


More information
----------------
* Module developed and tested with Odoo version 10.0
* For questions, please contact our support services
(support@savoirfairelinux.com)


Roadmap
-------
This module is financed and answered to customer needs.

It should be improve:
* add parameters in the user's interface to set the field wanted in comparison
