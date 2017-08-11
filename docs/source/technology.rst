Technology
==========

.. warning::
    The following is in the moment not implemented!
    But already written here that a lot of things all still need to be done.

This page is meant to describe the development stack for PyUniProt, and should be a useful introduction for contributors.

Versioning
----------

PyUniProt is kept under version control on GitHub. This allows for changes in the software to be tracked over time, and
for tight integration of the management aspect of software development. Code will be in future produced following the
Git Flow philosophy, which means that new features are coded in branches off of the development branch and merged
after they are triaged. Finally, develop is merged into master for releases. If there are bugs in releases that
need to be fixed quickly, "hot fix" branches from master can be made, then merged back to master and develop after
fixing the problem.

Testing in PyUniProt
--------------------
PyUniProt is written with unit testing. Whenever possible, PyUniProt will prefers to practice test-
driven development. This means that new ideas for functions and features are encoded as blank classes/functions and
directly writing tests for the desired output. After tests have been written that define how the code should work,
the implementation can be written.

Test-driven development requires us to think about design before making quick and dirty implementations. This results in
better code. Additionally, thorough testing suites make it possible to catch when changes break existing functionality.

Tests are written with the standard :code:`unittest` library.

Tox
~~~
While IDEs like PyCharm provide excellent testing tools, they are not programmatic.
`Tox <https://tox.readthedocs.io/en/latest/>`_ is python package that provides
a CLI interface to run automated testing procedures (as well as other build functions, that aren't important to explain
here). In PyBEL, it is used to run the unit tests in the :code:`tests` folder with the :code:`py.test` harness. It also
runs :code:`check-manifest`, builds the documentation with :code:`sphinx`, and computes the code coverage of the tests.
The entire procedure is defined in :code:`tox.ini`. Tox also allows test to be done on many different versions of
Python.

Continuous Integration
~~~~~~~~~~~~~~~~~~~~~~
Continuous integration is a philosophy of automatically testing code as it changes. PyUniProt makes use of the Travis CI
server to perform testing because of its tight integration with GitHub. Travis automatically installs git hooks
inside GitHub so it knows when a new commit is made. Upon each commit, Travis downloads the newest commit from GitHub
and runs the tests configured in the :code:`.travis.yml` file in the top level of the PyUniProt repository. This file
effectively instructs the Travis CI server to run Tox. It also allows for the modification of the environment variables.
This is used in PyUniProt to test many different versions of python.

Code Coverage
~~~~~~~~~~~~~
Is not implemented in the moment, but will be added in the next months.

Distribution
------------

Versioning
~~~~~~~~~~
PyUniProt tries to follow in future the following philosophy:

PyUniProt uses semantic versioning. In general, the project's version string will has a suffix :code:`-dev` like in
:code:`0.3.4-dev` throughout the development cycle. After code is merged from feature branches to develop and it is
time to deploy, this suffix is removed and develop branch is merged into master.

The version string appears in multiple places throughout the project, so BumpVersion is used to automate the updating
of these version strings. See .bumpversion.cfg for more information.

Deployment
~~~~~~~~~~
Code for PyUniProt is open-source on GitHub, but it is also distributed on the PyPI (pronounced Py-Pee-Eye) server.
Travis CI has a wonderful integration with PyPI, so any time a tag is made on the master branch (and also assuming the
tests pass), a new distribution is packed and sent to PyPI. Refer to the "deploy" section at the bottom of the
:code:`.travis.yml` file for more information, or the Travis CI PyPI
`deployment documentation <https://docs.travis-ci.com/user/deployment/pypi/>`_.
As a side note, Travis CI has an encryption tool so the password for the PyPI account can be displayed publicly
on GitHub. Travis decrypts it before performing the upload to PyPI.
