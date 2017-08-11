Query
=====

.. contents::

Examples
--------

For all string parameters you can use % as wildcard (please check the documentation below). All methods
have a parameter ``limit`` which allows to limit the number of results and ``as_df`` which allows to return
a `pandas.DataFrame`.

Initialize query object

.. code-block:: python

    import pyuniprot
    pyuniprot.update(taxids=[9606,10090,10116]) # human, mouse, rat update
    query = pyuniprot.query()

Methods by examples
-------------------

search for ...

human proteins with gene name 'TP53' (taxid=9606)
    >>> query.entry(gene_name='TP53', taxid=9606)
    [Cellular tumor antigen p53]

human proteins with *recommended full name* starts with 'Myeloid cell surface' (use % at the end)
    >>> query.entry(recommended_full_name='Myeloid cell surface%', taxid=9606)
    [Myeloid cell surface antigen CD33]


find all UniProt entries where the recommended full name contains 'CD33' (% at the start and end of search term) and
return as `pandas.DataFrame`

.. code-block:: python

    >>> results = query.entry(name='%CD33%', taxid=9606, as_df=True)
    # get first 2 lines of results with columns 'name','recommended_full_name', 'taxid'
    >>> my_results_as_data_frame.ix[:2,('name','recommended_full_name', 'taxid')]
              name                     recommended_full_name  taxid
    0   CD33_HUMAN         Myeloid cell surface antigen CD33   9606
    1  CCD33_HUMAN  Coiled-coil domain-containing protein 33   9606

find entries by a list of gene names

.. code-block:: python

    >>> query.entry(name=('TREM2_HUMAN', 'CD33_HUMAN'))
    [Myeloid cell surface antigen CD33, Triggering receptor expressed on myeloid cells 2]


If an attribute ends of an **s** it a clear hint that this is an 1:n or n:m relationship like keywords. There could
be several proteins linked to a keyword, but also several keywords are linked to one protein. Next lines of code shows
how to query for all proteins linked to the keyword 'Neurodegenaration' and returns the gene names.

.. code-block:: python

    >>> results = query.entry(keywords='Neurodegeneration')
    >>> len(results) # number of results
    322
    >>> [x.gene_name for x in results][:3] # show only the first 2 gene names
    ['CHMP1A', 'CLN3', 'COQ8A']

Every element in the list represents a `pyuniprot.manager.models.Entry` instance:

.. code-block:: python

    >>> first_protein = results[0] # fetch first result
    >>> type(first_protein)
    pyuniprot.manager.models.Entry
    >>> first_protein
    Charged multivesicular body protein 1a
    # get first 3 of all other keywords to this protein
    >>> first_protein.keywords[:3]
    [Reference proteome:KW-1185, Coiled coil:KW-0175, Repressor:KW-0678]


Properties
----------

.. code-block:: python

    q.gene_forms
    q.interaction_actions
    q.actions
    q.pathways

Query Manager Reference
-----------------------

.. autoclass:: pyuniprot.manager.query.QueryManager
    :members:

