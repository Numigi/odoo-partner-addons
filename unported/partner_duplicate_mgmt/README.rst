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


Preserved Partner:  Agrolait, Michel Fletcher

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


Merging Partners
----------------
It is possible to merge partners that are either both companies or both contacts.


Merging Contacts with Account Moves
-----------------------------------
To merge contacts that are linked to account moves, the user must be part of the group
"Contacts Merge With Account Moves", if not the merger won't be possible.


Adjusting the list of fields
----------------------------
The list of fields that appear in the merge wizard is configurable from the menu
Contacts -> Duplicate Management -> Partner Duplicate Fields.


Adjusting the similarity level
------------------------------
The similarity of two strings is computed using a trigram index.
There are 3 levels of similarity:

+------------------------------+--------------------+---------------------+
+Name of the system parameter  | Default Value      | String length       |
+==============================+====================+=====================+
+partner_name_similarity_1     | 0.5                | Between 0 and 9     |
+------------------------------+--------------------+---------------------+
+partner_name_similarity_2     | 0.6                | Between 10 and 17   |
+------------------------------+--------------------+---------------------+
+partner_name_similarity_3     | 0.7                | More than 18        |
+------------------------------+--------------------+---------------------+

The level of similarity required so that 2 partners whose names length are less than 9
are considered duplicates is 0.5 by default.
These values may be changed in system parameters.

Dependencies
------------
The module uses trigrams to compare names of partners. The postgresql extension pg_trgm is required for this purpose.
If your Odoo user is not superuser on the database (which is mostlikely the case in production), the module might
not install properly.

In order to install the extension, you may log in to your database as superuser and run:

> CREATE EXTENSION pg_trgm

Roadmap
-------
This module is financed and answered to customer needs.

* Add parameters in the user's interface to set the field wanted in comparison

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Yasmine El Mrini (yasmine.elmrini@savoirfairelinux.com)

More information
----------------
* Meet us at https://bit.ly/numigi-com

