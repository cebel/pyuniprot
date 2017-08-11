Installation
============

System requirements
-------------------

Because of the rich content of UniProt `PyUniProt` will create already for human, mouse and rat more than 5.7 million rows 
(08-04-017) with ~0.5 GiB of disk storage (depending on the used RDMS). Full installation (all organisms) will will 
need more than 5 GiB of disk storage. 

Tests were performed on *Ubuntu 16.04, 4 x Intel Core i7-6560U CPU @ 2.20Ghz* with
*16 GiB of RAM*. In general PyUniProt should work also on other systems like Windows, 
other Linux distributions or Mac OS.

.. _rdbms:

Supported databases
-------------------

`PyUniProt` uses `SQLAlchemy <http://sqlalchemy.readthedocs.io>`_ to cover a wide spectrum of RDMSs
(Relational database management system). For best performance MySQL or MariaDB is recommended. But if you have no
possibility to install software on your system SQLite - which needs no further
installation - also works. Following RDMSs are supported (by SQLAlchemy):

1. Firebird
2. Microsoft SQL Server
3. MySQL / `MariaDB <https://mariadb.org/>`_
4. Oracle
5. PostgreSQL
6. SQLite
7. Sybase

Install software
----------------

The following instructions are written for Linux/MacOS. The way you install python software on Windows could be a
little bit different.

In general there are 2 ways to install the software:

1. Using stable version from pypi
2. Using latest development version from github

Please note that option number 2 is only recommended for experienced programmers interested in the source code. Also
this software version is in development stage and we can not guarantee that the software is stable.

Often is make sense to avoid conflicts with other python installations by using different virtual environments. More
information about an easy way to manage different virtual environments you find
`here <http://virtualenvwrapper.readthedocs.io/en/latest/install.html>`_.

* If you want to install `pyuniprot` system wide use superuser (sudo for Ubuntu):

.. code-block:: bash

    sudo pip install pyuniprot

* If you have no sudo rights install as user

.. code-block:: bash

    pip install --user pyuniprot

* If you want to make sure you install `pyuniprot` in python3 environment:

.. code-block:: bash

    sudo python3 -m pip install pyuniprot

* If you are an experienced python with interest in the latest development version, clone and install from github

.. code-block:: bash

    git clone https://github.com/cebel/pyuniprot.git
    cd pyuniprot
    pip install -e .

MySQL/MariaDB setup
~~~~~~~~~~~~~~~~~~~
In general you don't have to setup any database, because by default `pyuniprot` uses file based SQLite. But we strongly
recommend to use MySQL/MariaDB.

Log in MySQL/MariaDB as root user and create a new database, create a user, assign the rights and flush privileges.

.. code-block:: mysql

    CREATE DATABASE pyuniprot CHARACTER SET utf8 COLLATE utf8_general_ci;
    GRANT ALL PRIVILEGES ON pyuniprot.* TO 'pyuniprot_user'@'%' IDENTIFIED BY 'pyuniprot_passwd';
    FLUSH PRIVILEGES;

Start a python shell and set the MySQL configuration. If you have not changed anything in the SQL statements ...

.. code-block:: python

    import pyuniprot
    pyuniprot.set_mysql_connection()

If you have used you own settings, please adapt the following command to you requirements.

.. code-block:: python

    import pyuniprot
    pyuniprot.set_mysql_connection()
    pyuniprot.set_mysql_connection(host='localhost', user='pyuniprot_user', passwd='pyuniprot_passwd', db='pyuniprot')

Updating
~~~~~~~~
The updating process will download a gzipped file provided by the UniProt team on the
`download page <http://www.uniprot.org/downloads>`_

Please note that download file needs ~700 Mb of disk space and the update can take several hours
(depending on your system). With every update a new database will created.

.. code-block:: python

    import pyuniprot
    pyuniprot.update()

To make sure that the latest UniProt version is used, use the parameter `force_download`

.. code-block:: python

    import pyuniprot
    pyuniprot.update(force_download=True)

Changing database configuration
-------------------------------

Following functions allow to change the connection to you RDBMS (relational database management system). Next
time you will use :code:`pyuniprot` by default this connection will be used.

To set a new MySQL/MariaDB connection ...

.. code-block:: python

    import pyuniprot
    pyuniprot.set_mysql_connection(host='localhost', user='pyuniprot_user', passwd='pyuniprot_passwd', db='pyuniprot')

To set connection to other database systems use the `pyuniprot.set_connection` function.

For more information about connection strings go to
the `SQLAlchemy documentation <http://docs.sqlalchemy.org/en/latest/core/engines.html>`_.

Examples for valid connection strings are:

- mysql+pymysql://user:passwd@localhost/database?charset=utf8
- postgresql://scott:tiger@localhost/mydatabase
- mssql+pyodbc://user:passwd@database
- oracle://user:passwd@127.0.0.1:1521/database
- Linux: sqlite:////absolute/path/to/database.db
- Windows: sqlite:///C:\\path\\to\\database.db

.. code-block:: python

    import pyuniprot
    pyuniprot.set_connection('oracle://user:passwd@127.0.0.1:1521/database')
