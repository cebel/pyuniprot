Benchmarks
==========

All benchmarks created on a standard notebook:

- OS: Linux Ubuntu 16.04.2 LTS (xenial)
- Python: 3.5.2
- Hardware: x86_64, Intel(R) Core(TM) i7-6560U CPU @ 2.20GHz, 4 CPUs, Mem 16Gb
- MariaDB: Server version: 10.0.29-MariaDB-0ubuntu0.16.04.1 Ubuntu 16.04

MySQL/MariaDB
-------------

Database created with following command in MySQL/MariaDB as root:

.. code:: sql

    CREATE DATABASE pyuniprot CHARACTER SET utf8 COLLATE utf8_general_ci;

User created with following command in MySQL/MariaDB:

.. code:: sql

    GRANT ALL PRIVILEGES ON pyuniprot.* TO 'pyuniprot_user'@'%' IDENTIFIED BY 'pyuniprot_passwd';
    FLUSH PRIVILEGES;

Import of UniProt for human, mouse and rat (NCBI taxonomy IDs: 9606, 10090, 10116 ) data executed with:

.. code:: python

    import pyuniprot
    pyuniprot.set_mysql_connection()
    pyuniprot.update(taxids=[9606, 10090, 10116])
    
- CPU times: user 2h 5min 11s, sys: 35.8 s, total: 2h 5min 47s

