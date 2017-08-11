Query functions
===============

.. contents::

Before you query
----------------

1. You can use % as a wildcard.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    # exact search
    query.entry(recommended_name='Amyloid beta A4 protein')

    # starts with 'Amyloid beta'
    query.entry(recommended_name='Amyloid beta%')

    # ends with 'A4 protein'
    query.entry(recommended_name='%A4 protein')

    # contains 'beta A4'
    query.entry(recommended_name='%beta A4%')

2. `limit` to restrict number of results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.entry(limit=10)

Use an offset by paring a tuple `(page_number, number_of_results_per_page)` to the parameter `limit`.

`page_number` starts with 0!

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    # first page with 3 results (every page have 3 results)
    query.entry(limit=(0,3))
    # fourth page with 10 results (every page have 10 results)
    query.entry(limit=(4,10))


3. Return :class:`pandas.DataFrame` as result
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is very useful if you want to profit from amazing pandas functions.

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.entry(as_df=True)


4. show all columns as dict
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    first_entry = query.entry(limit=1)[0]
    first_entry.__dict__

5. Return single values with key name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.entry(recommended_full_name='%kinase')[0].recommended_full_name

6. Access to the linked data models (1-n, n-m)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For example entry can access

- sequence
- accessions
- organism_hosts
- features
- functions
- ec_numbers
- db_references
- alternative_full_names
- alternative_short_names
- disease_comments
- tissue_specificities
- other_gene_names

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    r = query.entry(limit=1)[0]

    r.sequence
    r.accessions
    r.organism_hosts
    r.features
    r.functions
    r.ec_numbers
    r.db_references
    r.alternative_full_names
    r.alternative_short_names
    r.disease_comments
    r.tissue_specificities
    r.other_gene_names

But from EC number you can go back to entry

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    r = query.ec_number(ec_number='1.1.1.1')
    [x.entry for x in r]
    # following is crazy but possible, again go back to ec_number
    [x.entry.ec_numbers for x in r]

7. Entry name is available in almost all methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In almost all function you have the parameter `entry_name` (primary key for UniProt entries) even it is not part of the
model.

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.other_gene_name(entry_name='A4_HUMAN')

entry
-----
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.entry(name='1433E_HUMAN', recommended_full_name='14-3-3 protein epsilon', gene_name='YWHAE')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.entry` for all available parameters.

disease
-------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.disease(acronym='AD')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.disease` for all available parameters.

disease_comment
---------------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.disease_comment(comment='%Alzheimer%')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.disease_comment` for all available parameters.

other_gene_name
---------------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.other_gene_name(entry_name='A4_HUMAN'))

Check documentation of :func:`pyuniprot.manager.query.QueryManager.other_gene_name` for all available parameters.

alternative_full_name
---------------------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.alternative_full_name(name='Alzheimer disease amyloid protein')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.alternative_full_name` for
all available parameters.

alternative_short_name
----------------------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.alternative_short_name(name='Alzheimer disease amyloid protein', entry_name='A4_HUMAN')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.alternative_short_name` for all
available parameters.

accession
---------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.accession(accession='P05067', entry_name='A4_HUMAN')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.accession` for all available parameters.

pmid
----
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.pmid(pmid=7644510)

Check documentation of :func:`pyuniprot.manager.query.QueryManager.pmid` for all available parameters.

organismHost
------------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.organism_host(taxid=9606)
    # 0 results if you have only installed human

Check documentation of :func:`pyuniprot.manager.query.QueryManager.organismHost` for all available parameters.

dbReference
-----------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.db_reference(type_='EMBL', identifier='U20972')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.dbReference` for all available parameters.

feature
-------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.feature(type_='sequence variant', limit=1)

Check documentation of :func:`pyuniprot.manager.query.QueryManager.feature` for all available parameters.

function
--------
.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.function(text='%Alzheimer%')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.function` for all available parameters.

keyword
-------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    r = query.keyword(name='Phagocytosis')[0]
    [x.entry for x in r] # all proteins linked to keyword Phagocytosis

Check documentation of :func:`pyuniprot.manager.query.QueryManager.keyword` for all available parameters.

ec_number
---------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.ec_number(ec_number='1.1.1.1')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.ec_number` for all available parameters.

subcellular_location
--------------------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.subcellular_location(location='Autophagosome lumen')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.subcellular_location` for all available
parameters.

tissue_specificity
------------------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.tissue_specificity(comment='%brain%', limit=1)

Check documentation of :func:`pyuniprot.manager.query.QueryManager.tissue_specificity` for all available
parameters.

tissue_in_reference
-------------------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()

    query.tissue_in_reference(tissue: 'Substantia nigra')

Check documentation of :func:`pyuniprot.manager.query.QueryManager.tissue_in_reference` for all available
parameters.

Query properties
================

dbreference_types
-----------------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()
    query.dbreference_types

taxids
------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()
    query.taxids

datasets
--------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()
    query.datasets

feature_types
-------------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()
    query.feature_types

subcellular_locations
---------------------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()
    query.subcellular_locations

tissues_in_references
---------------------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()
    query.tissues_in_references

keywords
--------

.. code-block:: python

    import pyuniprot
    query = pyuniprot.query()
    query.keywords
