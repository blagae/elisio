## Back-end

Elisio's back-end requires the following prerequisites to be fulfilled on the machine it will run on.

* Python 3.x must be installed with access to `pip`
* all packages in requirements.txt must be installed - this can be handled by a virtual environment

## Virtual environment

We advise you to create a Python virtual environment for this project,
in order not to get into version trouble in case you are working on or running other Python projects on the same machine.
The packages listed in requirements.txt should be enough to have virtualenv construct a working environment for Elisio.
You can find more info about virtualenv [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

## Tests

We have a large number of tests for the different levels of the verse scanning process.

All tests should succeed in develop's HEAD revision at all times.
