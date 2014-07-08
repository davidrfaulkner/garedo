guredo
======

Basic Python 2 / pyqt / sqlite3 application for administration of martial arts gradings.

Allows students basic data to be keyed in and stored.

Fees calculated based on grade attempted.

Total fees including seperate belt fee.

Dojos can be loaded from external file.

Pricing can be loaded from external file.

Report exports, including a basic format for doing a certificate template mail merge.

Application should work on Windows, Mac OS X and Linux.


Installation (Windows)
======================

Instructions tested on Windows 7.

1. Install python (Windows use https://www.python.org/download/releases/2.7.8/ )
2. Install pyqt using minimal install option (Windows use http://www.riverbankcomputing.co.uk/software/pyqt/download - under binary package section)
3. Double click guredo.pyw icon and it should work (you have presumably copied the files somewhere)


Config Files
============

config.json is a JSON file for config data (currently Belt Price, Grading Fees, and Dojo list)

config.json.default is a backup copy of the config file, and represents a fairly empty state

The config files are strictly read by the program, so have to be correct. Basic JSON rules below.

    Data is represented in name/value pairs

    Curly braces hold objects and each name is followed by ':'(colon), the name/value pairs are separated by , (comma). The last item does NOT have a trailing comma.

    Square brackets hold arrays and values are separated by ,(comma). The last item does NOT have a trailing comma.



Files
============

readme files are for reading

guredo.pyw is the application.

gradings.db is the database for ALL grading dates recorded. If you rename or delete it, the application will build a new empty one.

guredo_debug.log contains errors / debug info when errors are encountered.

Files in /template are files that should not be adjusted unless you know what you are doing.
It includes the mail merge template, and text files to populate dojo list and prices

Files in /export are files the application generates when you do exports / reports.
You shouldnt need to browse here as the application will try launch these files for you when they are made.
This folder will also include a temp copy of the mailmerge template, re-created each time a certificate export is done.


Dev Files
=========

Files in /bin are python files to support guredo.

guredo.xpyqt is a project file for editing the project in Monkey Studio IDE

mainwindow.ui is a Qt Designer file, which builds the user interface

