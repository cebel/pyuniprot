PyUniProt |stable_build|
====================

|stable_documentation| |pypi_license|

`PyUniProt <http://pyUniProt.readthedocs.io>`_ is a Python package
to access and query chemical–gene/protein interactions, chemical–disease and gene–disease
relationships by data provided by the `Comparative Toxicogenomics Database <http://ctdbase.org>`_ .
Data are installed in a (local or remte) RDBMS enabling bioinformatic algorithms very fast response times
to sophisticated queries and high flexibility by using SOLAlchemy database layer.
PyUniProt is developed by the
`Department of Bioinformatics <https://www.scai.fraunhofer.de/en/business-research-areas/bioinformatics.html>`_
at the Fraunhofer Institute for Algorithms and Scientific Computing
`SCAI <https://www.scai.fraunhofer.de/en.html>`_
For more in for information about CTD go to
`this section in the documentation <http://pyUniProt.readthedocs.io/en/latest/ctd.html>`_.

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
    - just test pyUniProt, but don't want to spend time in setting up a database

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
The updating process will download the *uniprot_sprot.xml.gz* provided by the UniProt team on ftp server
`download page <ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/>`_

.. warning:: Please note that files needs more than 6 Gb of disk space and the update takes ~2h only for human
(`pyuniprot.update(` ; depending on your system)

It is strobgly recommended to restrict the entries in the database by parsing a list of NCBI Taxonomy IDs to the
parameter taxids. To find out the correct NCBI Taxonomy ID please go to
`NCBI Taxonomy web form <https://www.ncbi.nlm.nih.gov/taxonomy/>`_. In the following example we use 9606 as identifier
for Homo sapiens, 10090 for Mus musculus and 10116 for Rattus norvegicus.

.. code-block:: python

    import pyuniprot
    pyuniprot.update(taxids=[9606, 10090, 10116])

If you want to load all UniProt entries in the database:

.. code-block:: python

    import pyuniprot
    pyuniprot.update()

Test a query function
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    >>> query = pyuniprot.query()
    >>> results =query.get_chem_gene_interaction_actions(gene_name='APP', interaction_action='meman%', limit=1)
    >>> first_result = r
    >>> r.chemical
    Memantine
    >>> r.pubmed_ids
    [21290839]
    >>> r.chemical.drugbank_ids
    [DB014043]


More information
----------------
See the `installation documentation <http://pyUniProt.readthedocs.io/en/latest/installation.html>`_ for more advanced
instructions. Also, check the change log at :code:`CHANGELOG.rst`.

CTD tools and licence (use of data)
-----------------------------------
CTD provides also many online `query interfaces <http://ctdbase.org/search/>`_ and
`tools to analyse data <http://ctdbase.org/tools/>`_ on their website.

Please be aware of the `CTD licence <http://ctdbase.org/about/legal.jsp>`_ which allows the use of data only for
research and educational purposes. Medical treatment decisions should not be made based on the information in CTD.

Any reproduction or use for commercial purpose is prohibited without the prior express written permission of the
MDI Biological Laboratory and NC State University.


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

.. |phago_logo| image:: https://owncloud.scai.fraunhofer.de/index.php/apps/files_sharing/ajax/publicpreview.php?x=1920&y=562&a=true&file=phago-logo.jpg&t=7llp11KwSiuXYOh&scalingup=0
    :target: https://www.imi.europa.eu/content/phago
    :alt: PHAGO project logo

.. |aetionomy_logo| image:: https://owncloud.scai.fraunhofer.de/index.php/apps/files_sharing/ajax/publicpreview.php?x=1920&y=562&a=true&file=aetionomy-logo.png&t=5ClUGTZRAYkeb7m&scalingup=0
    :target: http://www.aetionomy.eu/en/vision.html
    :alt: AETIONOMY project logo

.. |imi_logo| image:: https://owncloud.scai.fraunhofer.de/index.php/apps/files_sharing/ajax/publicpreview.php?x=1920&y=562&a=true&file=imi-logo.png&t=Uvw79bTxGyd07oo&scalingup=0
    :target: https://www.imi.europa.eu/
    :alt: IMI project logo

.. |scai_logo| image:: https://owncloud.scai.fraunhofer.de/index.php/apps/files_sharing/ajax/publicpreview.php?x=1920&y=562&a=true&file=scai-logo.png&t=fyJo2GzFDLNypho&scalingup=0
    :target: https://www.scai.fraunhofer.de/en/business-research-areas/bioinformatics.html
    :alt: SCAI project logo

.. |er_model| image:: https://owncloud.scai.fraunhofer.de/index.php/apps/files_sharing/ajax/publicpreview.php?x=1920&y=562&a=true&file=pyuniprot_er_model.png&t=QUm8KPPnNGoH8wp&scalingup=0
    :target: http://pyuniprot.readthedocs.io/en/latest/
    :alt: Entity relationship model