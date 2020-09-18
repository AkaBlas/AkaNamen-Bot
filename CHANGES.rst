=========
Changelog
=========

Version 1.1.1
=============
*Released 2020-09-18*

*Changes and bug fixes for the user experience:*

- Improve Highscore Texts (`#74`_)
- Improve Inline Mode (`#73`_)
- Fix vCard for no housenumber (`#72`_)

*Other changes and bug fixes:*

- Copy ``UserScore`` in /rebuild (`#71`_)
- Fix Gender Equality Check in ``AttributeManagers`` (`#70`_)
- Fix Links in Changelog (`#69`_)

.. _`#74`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/74
.. _`#73`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/73
.. _`#72`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/72
.. _`#71`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/71
.. _`#70`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/70
.. _`#69`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/69

Version 1.1
===========
*Released 2020-09-17*

*Changes and bug fixes for the user experience:*

- Improve Parsing of Addresses (`#62`_)
- Move Fetching TG Profile Picture to Editing Conversation (`#61`_)
- Add Conductor to Allowed Instruments (`#56`_)
- Fix Interrupting of Free Text Games (`#55`_)
- Fix Typos (`#54`_)
- Link Info Channel in Readme and Preview it in Docs (`#52`_)

*Changes and bug fixes for the admin experience:*

- Add ``/rebuild`` command for Admin (`#63`_)
- Stabilize Registration Process (`#60`_)

*Changes fixes and bugfixes to the backend:*

- Gender Photo Questions (`#63`_)
- Copy Members with ``deepcopy()`` (`#59`_)

.. _`#62`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/62
.. _`#61`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/61
.. _`#56`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/56
.. _`#55`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/55
.. _`#54`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/54
.. _`#52`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/52
.. _`#63`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/63
.. _`#60`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/60
.. _`#59`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/59

Version 1.0
===========
*Released 2020-09-16*

*Changes and bug fixes for the user experience:*

- Add Headings to Game Setup (`#43`_)
- Add Statistics (`#42`_)
- Add some FAQ (`#41`_)
- Improve Wording of Questions (`#39`_)
- Fix ``UserScore.add_to_score()`` and /highscore Command (`#38`_)
- Fix Bugs in Editing Conversation (`#35`_)
- Allow Admins to see all User Data through Inline Mode (`#34`_)
- Fix nightly Check of User Status(`#33`_)
- Fix "Alle" Button for Question Attributes (`#26`_)

*Bug fixes and changes to the backend:*

- Exclude Player from Possible Hints (`#46`_)
- Tweak Performance (`#44`_)
- Overhaul ``AttributeManager`` Logic and Game Setup (`#40`_)
- Run Docs Workflow on ``Py3.8`` (`#36`_)

.. _`#43`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/43
.. _`#42`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/42
.. _`#41`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/41
.. _`#39`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/39
.. _`#38`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/38
.. _`#35`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/35
.. _`#34`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/34
.. _`#33`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/33
.. _`#26`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/26
.. _`#46`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/46
.. _`#44`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/44
.. _`#40`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/40
.. _`#36`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/36

Version RC2
===========
*Released 2020-09-06*

*Changes and bug fixes for the user experience:*

- Fix Formatting of Message to Admin in Registration Process (`#10`_)
- Fix Birthday not addable (`#12`_)
- Show Caption on Members Picture while editing (`#14`_)
- Fix Typos in editing conversation (`#18`_)
- Improve Highscore Layout (`#19`_)
- Comment on /hilfe command in welcome message (`#23`_)
- Fix Spelling of Foto (`#24`_)

*Bug fixes and changes to the backend:*

- Rework Backend (`#25`_)
- Don't loose + in Phone Numbers (`#20`_)
- Check if update is None in error handler (`#17`_)
- Improve Internals of ``Member._get_akadressen()`` (`#13`_)

.. _`#10`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/10
.. _`#12`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/12
.. _`#14`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/14
.. _`#18`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/18
.. _`#19`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/19
.. _`#23`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/23
.. _`#24`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/24
.. _`#25`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/25
.. _`#20`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/20
.. _`#17`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/17
.. _`#13`: https://github.com/Bibo-Joshi/AkaNamen-Bot/pull/13


Version RC1
===========
*Released 2020-08-29*

First release candidate. Adds initial setup for frontend and backend as well as documentation.
