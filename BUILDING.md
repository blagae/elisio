# Building the Elisio Project

The Elisio project combines a number of technologies, and thus requires that programs providing support for these technologies be installed on your system.

## Database

It is possible to run Elisio without connecting to a database server, by using the SQLite implementation of Python itself.
However, the write phase of the method test_hexameter_scan_all will be horribly slow (300 verses per minute) during the first test run.
With Postgres or MySQL, you can get performance up to 5000 verses per minute.

If you do want to use a database server, you are constrained by the possibilities offered by Django and Python 3:
* PostgreSQL: requires the `psycopg2` package. Actively supported.
* MySQL: requires the `pymysql` package. Supported, but not tested extensively.
* Oracle DB: should be supported, but has not been tested.
* Others: support in Django varies significantly (use at own risk)

Basically, you should get good performance with PostgreSQL, and Django also implicitly advises users to use that database.
Unless a compelling reason to change comes up, Postgres will be used in the reference implementation.

## Back-end

Elisio's back-end requires the following prerequisites to be fulfilled on the machine it will run on.

* Python 3.x must be installed with access to `pip`
* all packages in requirements.txt must be installed - this can be handled by a virtual environment
* you must have a file `Elisio/Elisio/local.py` (copy from `local_template.py`) with a number of properties specified. 
If this condition is not fulfilled, you will get error messages very early in your build process.
* for the web app deployment, you will need to allow traffic to a network port for incoming requests

### Virtual environment

We advise you to create a Python virtual environment for this project,
in order not to get into version trouble in case you are working on or running other Python projects on the same machine.
The packages listed in requirements.txt should be enough to have virtualenv construct a working environment for Elisio.
You can find more info about virtualenv [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

### Generating local.py

You can create `local.py` by copying it from `local_template.py`. This file contains your database properties and a few other settings,
so that you can keep your passwords etc private. `local.py` will be ignored by git since it's explicitly listed in the .gitignore file,
but it remains your responsibility to make sure that your private connection data is never added to git and/or published.

If you don't create `local.py`, or don't create it correctly, then Elisio will refuse to run.

### First run

Once you've configured `local.py`, you should run the migrate command. From the folder containing `manage.py`, run this command:

```bash
$ python manage.py migrate
```

This will create your database schema and load all available verses and metadata from the source files (fixtures) into the database.
Elisio contains an algorithm for remembering the syllable structures of successfully parsed verses in the database.
This table will be filled during the first run of the test suite on a fresh database, when running `test_hexameter_scan_all`.

### Tests

We have a large number of tests for the different levels of the verse scanning process.

All tests should succeed in develop's HEAD revision at all times, except `test_hexameter_scan_for_debug`
which might accidentally contain a failing verse (i.e. not cleaned up between debugging & committing).
Please try to avoid this, because succeeding builds are so much more fulfilling, but it's not a huge problem.
You may also notice in the version history that I have committed very often with a failing verse number in this method.

The longest-running test is `test_hexameter_scan_all`, which will take a while during the first run if you're on SQLite.
On subsequent runs, you'll get performance comparable to Postgres and presumably the other DBMS.

Since git commit `596adfe1`, you will probably need the folder containing `git.sh` or `git.exe` on the path of your OS.
More investigation is needed as to how common this is and how to make the code work across different hosts.

## Front-end

Since April 2018, we have started working on using a front-end (JavaScript) framework for the web app of Elisio,
rather than just hacking together some JQuery. We are hopeful that this will greatly improve the quality of the web app,
but it also requires some more set-up than just manually adding `<script>` tags.

Additionally, we chose not to use vanilla JavaScript but went with TypeScript,
a superset of JavaScript which allows writing object-oriented code and using a full type system.

### Installation

You need a modern version of the Node Package Manager, which comes packaged with Node https://nodejs.org/en/
In addition, you'll need to head to the typescript folder in the project and install Elisio's JavaScript prerequisites.

```bash
path/to/elisio $ cd Elisio/Elisio/typescript
path/to/elisio/Elisio/Elisio/typescript $ npm install
```

### TypeScript

Most browsers cannot parse native TypeScript, so your code must be transpiled to vanilla JavaScript.
This is done by `tsc`, a tool supplied by Microsoft for that exact purpose.

If you're working from the terminal, then you can run the following command to have the tool watch for changes in your .ts files
and automatically compile any time you make edits.

```
path/to/elisio/Elisio/Elisio/typescript $ tsc -w
```

If you're using an IDE, then you should be able to find an option that will automatically run the `tsc` tool.
In PyCharm, this is an option in Settings > Languages and Frameworks > TypeScript > 'Recompile on changes'.

FYI we have configured that all output code, in the JavaScript language, be added to the folder `typescript/src`.

### Deploying

We tried to simplify building the front-end code package by using the Node tool `webpack`, which collates all code in a single JavaScript file
that can then easily be added to the web page.
That JavaScript file is called `bundle.js`, is virtually unreadable, and is embedded in the `base.html` template in the Django app.

In order to run the webpack, you can run either of the following commands from your terminal:

```
path/to/elisio/Elisio/Elisio/typescript $ npm run dev # for semi-readable JavaScript (for debugging)
path/to/elisio/Elisio/Elisio/typescript $ npm run build # for unreadable JavaScript (for production)
```

If you're using an IDE, then you can add either of these build scripts to your pre-deploy workflow.
In PyCharm, this is done by adding a pre-launch step "run NPM script" to your launch config with either `dev` or `build` as a script name.

## General remarks

### PTVS

Original development of Elisio took place with the Python Tools for Visual Studio (PTVS), which allows advanced Python editing from that IDE.
This has some minor side effects, most notably a `.sln` file and a `.pyproj` file, which you can safely ignore if you don't use PTVS.

Since 2017, the main developer of this project has abandoned PTVS for PyCharm, so these files are no longer fully up to date.
If you want to use PTVS, then you will need to edit the `.pyproj` file to reflect all the file additions/deletions/moves since we abandoned PTVS.
If you do this, then you're welcome to submit a pull request for the files that weren't added correctly.
You will be thanked heartily, and we can enjoy a hilarious conversation about the usability flaws of Visual Studio.
