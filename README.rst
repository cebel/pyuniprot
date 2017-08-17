|project_logo_large|

PyUniProt |stable_build|
========================

|stable_documentation| |pypi_license|

`PyUniProt <http://pyUniProt.readthedocs.io>`_ is a Python package
to access and query chemical–gene/protein interactions, chemical–disease and gene–disease
relationships by data provided by the European Bioinformatics Institute (EMBL-EBI),
the SIB Swiss Institute of Bioinformatics and the Protein Information Resource (PIR).

Data are installed in a (local or remote) RDBMS enabling bioinformatic algorithms very fast response times
to sophisticated queries and high flexibility by using SOLAlchemy database layer.
PyUniProt is developed by the
`Department of Bioinformatics <https://www.scai.fraunhofer.de/en/business-research-areas/bioinformatics.html>`_
at the Fraunhofer Institute for Algorithms and Scientific Computing
`SCAI <https://www.scai.fraunhofer.de/en.html>`_
For more in for information about pyUniProt go to
`the documentation <http://pyUniProt.readthedocs.io>`_.

|er_model|

This development is supported by following `IMI <https://www.imi.europa.eu/>`_ projects:

- `AETIONOMY <http://www.aetionomy.eu/>`_ and
- `PHAGO <http://www.phago.eu/>`_.

|imi_logo| |aetionomy_logo| |phago_logo| |scai_logo|

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

Getting Started
---------------
This is a quick start tutorial for impatient.

Installation |pypi_version| |python_versions|
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PyUniProt can be installed with `pip <https://pip.pypa.io/en/stable/>`_.

.. code-block:: bash

    pip install pyuniprot

If you fail because you have no rights to install use superuser (sudo on Linux before the commend) or ...

.. code-block:: bash

    pip install --user pyuniprot

If you want to make sure you are installing this under python3 use ...

.. code-block:: bash

    python3 -m pip install pyuniprot

SQLite
~~~~~~
.. note:: If you want to use SQLite as your database system, because you ...

    - have no possibility to use RDMSs like MySQL/MariaDB
    - just test PyUniProt, but don't want to spend time in setting up a database

    skip the next *MySQL/MariaDB setup* section. But in general we recommend MySQL or MariaDB as your RDBMS.

If you don't know what all that means skip the section *MySQL/MariaDB setup*.

Don't worry! You can always later change the configuration. For more information about
changing database system later go to the subtitle *Changing database configuration*
`Changing database configuration <http://pyuniport.readthedocs.io/en/latest/installation.html>`_
in the documentation on readthedocs.

MySQL/MariaDB setup
~~~~~~~~~~~~~~~~~~~
Log in MySQL as root user and create a new database, create a user, assign the rights and flush privileges.

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
The updating process will download the *uniprot_sprot.xml.gz* file provided by the UniProt team on their ftp server
`download page <ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/>`_

.. warning:: Please note that UniProt download file needs ~700 Mb of disk space and the update takes ~2h only for
human, mouse and rat (depending on your system)

It is strongly recommended to restrict the entries liked to specific organisms your are interested in by parsing a list
of NCBI Taxonomy IDs to the parameter `taxids`. To identify correct NCBI Taxonomy IDs please go to
`NCBI Taxonomy web form <https://www.ncbi.nlm.nih.gov/taxonomy/>`_. In the following example we use 9606 as identifier
for Homo sapiens, 10090 for Mus musculus and 10116 for Rattus norvegicus.

.. code-block:: python

    import pyuniprot
    pyuniprot.update(taxids=[9606, 10090, 10116])

If you want to load all UniProt entries in the database:

.. code-block:: python

    import pyuniprot
    pyuniprot.update()

The update uses the download if it still exists on you system (~/.pyuniprot/data/uniprot_sprot.xml.gz). If you use
the parameter `force_download` the current file from UniProt will be downloaded.

.. code-block:: python

    import pyuniprot
    pyuniprot.update(force_download=True)

Quick start with query functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Initialize the query object

.. code-block:: python

    query = pyuniprot.query()

Get all entries

.. code-block:: python

    all_entries = query.entry()


Use parameters like gene_name to find specific entries

.. code-block:: python

    >>> entry = query.entry(gene_name='YWHAE', taxid=9606, recommended_short_name='14-3-3E', name='1433E_HUMAN')[0]
    >>> entry
    14-3-3 protein epsilon

Entry is the root element in the database. Form here you can reach all other data
    >>> entry.accessions
    [P62258, B3KY71, D3DTH5, P29360, P42655, Q4VJB6, Q53XZ5, Q63631, Q7M4R4]
    >>> entry.functions
    ["Adapter protein implicated in the regulation of a large spectrum of both ..."]

If a parameter ends on a **s** you can search
    >>> alcohol_dehydrogenases = q.entry(ec_numbers='1.1.1.1')
    >>> [x.name for x in q.get_entry(ec_numbers='1.1.1.1')]
    ['ADHX_RAT', 'ADH1_RAT', 'ADHX_HUMAN', 'ADHX_MOUSE']
    >>> query.entry(ec_numbers=('1.1.1.1', '1.1.1.2'))
    ['Adh5', 'Adh1', 'ADH5', 'Adh5', 'Adh6', 'ADH7', 'Adh7', 'Adh7', 'Adh1']

As dataframe with a limit of 10 and accession number starts with Q9 (% used as wildcard)

.. code-block:: python

    >>> query.accession(as_df=True, limit=3, accession='Q9%')
       id accession  entry_id
    0   1    Q9CQV8         1
    1  32    Q9GIK8         6
    2  33    Q9TQB4         6



More information
----------------
See the `installation documentation <http://pyuniprot.readthedocs.io/en/latest/installation.html>`_ for more advanced
instructions. Also, check the change log at :code:`CHANGELOG.rst`.

UniProt tools and licence (use of data)
---------------------------------------
UniProt provides also many online `query interfaces <http://www.uniprot.org>`_ on their website.

Please be aware of the `UniProt licence <http://www.uniprot.org/help/license>`_.

Links
-----
Universal Protein Resource (UniProt)

- `UniProt website <http://www.uniprot.org/>`_
- `About UniProt <http://www.uniprot.org/help/about>`_

PyUniProt

- Documented on `Read the Docs <http://pyuniprot.readthedocs.io/>`_
- Versioned on `GitHub <https://github.com/cebel/pyuniprot>`_
- Tested on `Travis CI <https://travis-ci.org/cebel/pyuniprot>`_
- Distributed by `PyPI <https://pypi.python.org/pypi/pyuniprot>`_
- Chat on `Gitter <https://gitter.im/pyuniprot/Lobby>`_

.. |stable_build| image:: https://travis-ci.org/cebel/pyUniProt.svg?branch=master
    :target: https://travis-ci.org/cebel/pyuniprot
    :alt: Stable Build Status

.. |stable_documentation| image:: https://readthedocs.org/projects/pyUniProt/badge/?version=latest
    :target: http://pyuniprot.readthedocs.io/en/latest/
    :alt: Development Documentation Status

.. |pypi_license| image:: https://img.shields.io/pypi/l/PyUniProt.svg
    :alt: Apache 2.0 License

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/PyUniProt.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/PyUniProt.svg
    :alt: Current version on PyPI

.. |phago_logo| image:: https://raw.githubusercontent.com/cebel/pyuniprot/master/docs/source/_static/logos/phago_logo.jpeg
    :target: https://www.imi.europa.eu/content/phago
    :alt: PHAGO project logo

.. |aetionomy_logo| image:: https://raw.githubusercontent.com/cebel/pyuniprot/master/docs/source/_static/logos/aetionomy_logo.png
    :target: http://www.aetionomy.eu/en/vision.html
    :alt: AETIONOMY project logo

.. |imi_logo| image:: https://raw.githubusercontent.com/cebel/pyuniprot/master/docs/source/_static/logos/imi_logo.png
    :target: https://www.imi.europa.eu/
    :alt: IMI project logo

.. |scai_logo| image:: https://raw.githubusercontent.com/cebel/pyuniprot/master/docs/source/_static/logos/scai_logo.png
    :target: https://www.scai.fraunhofer.de/en/business-research-areas/bioinformatics.html
    :alt: SCAI project logo

.. |er_model| image:: https://owncloud.scai.fraunhofer.de/index.php/apps/files_sharing/ajax/publicpreview.php?x=1920&y=562&a=true&file=pyuniprot_er_model.png&t=QUm8KPPnNGoH8wp&scalingup=0
    :target: http://pyuniprot.readthedocs.io/en/latest/
    :alt: Entity relationship model

.. |project_logo_large| image:: https://raw.githubusercontent.com/cebel/pyuniprot/master/docs/source/_static/logos/project_logo_large.png
    :alt: Project logo