.. :changelog:

Release History
===============

0.33.0 (2017-11-01)
+++++++++++++++++++

**Features**

- add "required_resource_access" when applicable

**Bugfixes**

- Get/Delete of Users now encode for you if you provide the UPN.

0.32.0 (2017-09-22)
+++++++++++++++++++

**Features**

- Add Application.oauth2_allow_implicit_flow (create, update, get)
- Add to User: immutable_id, given_name, surname, user_type, account_enabled
- Add to UserCreate: given_name, surname, user_type, mail
- Add to UserUpdate: immutable_id, given_name, surname, user_type, user_principal_name

**Bugfixes**

- Renamed User.signInName to an array User.signInNames

0.31.0 (2017-08-09)
+++++++++++++++++++

- Add domains operation group
- Add usage locations to user
- Add several new attributes to AADObject

0.30.0 (2017-04-20)
+++++++++++++++++++

* ApiVersion is now 1.6 for the whole package
* This wheel package is now built with the azure wheel extension

0.30.0rc6 (2016-09-14)
++++++++++++++++++++++

**Bugfixes**

* 'list' methods returned only 100 entries (#653)

0.30.0rc5 (2016-06-23)
++++++++++++++++++++++

* Initial preview release
