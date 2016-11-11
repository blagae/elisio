Building the Elisio Project
===
In general, Elisio requires the following prerequisites to be fulfilled on the machine it will run on.

* Python 3.x must be installed with access to pip
* all packages in requirements.txt must be installed - this can be handled by a virtual environment
* you must have a file Elisio/Elisio/local.py (same folder as local_template.py) with a number of properties specified. 
If this condition is not fulfilled, you will get error messages very early in your build process.
* you must have access to a database server (possibly remote) or SQLite
* for the web app deployment, you will need to allow traffic to a network port for incoming requests

Virtual environment
===

We advise you to create a Python virtual environment for this project,
in order not to get into version trouble in case you are working on or running other Python projects on the same machine.
The packages listed in requirements.txt should be enough to have virtualenv construct a working environment for Elisio.
You can find more info about virtualenv on http://docs.python-guide.org/en/latest/dev/virtualenvs/

Generating local.py
===

You can create local.py by copying it from local_template.py . This file contains your database properties and a few other settings,
so that you can keep your passwords etc private. local.py will be ignored by git since it's explicitly listed in the .gitignore file,
but it remains your responsibility to make sure that your private data is not uploaded to the git hosting site.

If you don't create local.py, or don't create it correctly, then Elisio will refuse to run.

Database
===

It is possible to run Elisio without connecting to a database server, by using the SQLite implementation of Python itself.
However, the write phase of the method test_hexameter_scan_all will be horribly slow (3min per 1000 verses) during the first test run.

If you do want to use a database server, you are constrained by the possibilities offered by Django and Python 3:
* PostgreSQL: requires the psycopg2 package. Actively supported.
* MySQL: should be supported, but not tested. Connector situation for Python 3 is murky.
* Oracle DB: should be supported, but not tested.
* Others: support in Django varies significantly (use at own risk)

Basically, you should get good performance with PostgreSQL, and Django also implicitly advises users to use that database.
Unless my preferences change, Postgres will always be used in the reference implementation.

There is a minor glitch when combining Python 3.5 with psycopg2 2.6.1 in PTVS. So until a new psycopg2 version is released,
you may need to work with Python 3.4 (although YMMV).

First run
===

Once you've configured local.py, you should run the migrate command. From the folder containing manage.py, run this command:

```bash
$ python manage.py migrate
```

This will create your database schema and load all available verses and metadata from the source files into the database.
Elisio contains an algorithm for remembering the syllable structures of successfully parsed verses in the database.
This table will be filled during the first test run on a fresh database (with test_hexameter_scan_all).

Tests
===

We have a large number of tests for the different levels of the verse scanning process.

All tests should succeed in develop's HEAD revision at all times, except test_hexameter_scan_for_debug
which might accidentally contain a failing verse (i.e. not cleaned up between debugging & committing).
Please try to avoid this, because succeeding builds are so much more fulfilling, but it's not a huge problem.
You may also notice in the version history that I have committed very often with a failing verse number in this method.

The longest-running test is test_hexameter_scan_all, which will take a while during the first run if you're on SQLite.
On subsequent runs, you'll get performance comparable to Postgres and presumably the other dbms.

PTVS
===

Original development of Elisio took place with the Python Tools for Visual Studio (PTVS), which allows advanced Python editing from that IDE.
This has some minor side effects, most notably a .sln file and a .pyproj file, which you can safely ignore if you don't use PTVS.
If you push new files to the public git repository, then you may notice that some changes will be applied to these
files when the commits are being merged to the develop branch.
