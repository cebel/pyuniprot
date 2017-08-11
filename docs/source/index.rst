PyUniProt Documentation
=======================
for version: |version|


:code:`PyUniProt` is python software interface developed by the
`Department of Bioinformatics <https://www.scai.fraunhofer.de/en/business-research-areas/bioinformatics.html>`_
at the Fraunhofer Institute for Algorithms and Scientific Computing
`SCAI <https://www.scai.fraunhofer.de/en.html>`_
to the data provided by the `European Bioinformatics Institute (EMBL-EBI) <http://www.ebi.ac.uk/>`_ on their
`UniProt website <http://www.uniprot.org/uniprot/>`_.

The content of UniProt and the use of PyUniProt in combination with `PyBEL <https://pyuniprot.readthedocs.io/en/latest/>`_ supports
successfully scientists in the `IMI <https://www.imi.europa.eu/>`_ funded projects
`AETIONOMY <http://www.aetionomy.eu/>`_  and `PHAGO <https://www.imi.europa.eu/content/phago>`_
in the identification of potential drugs in complex disease networks with several thousands of
relationships compiled from `BEL <http://openbel.org/>`_ statements.

Aim of this software project is to provide an programmatic access to locally stored UniProt data and
allow a filtered export in several formats used in the scientific community. Many query functions allow search in the
data and use it as `pandas.DataFrame` in Jupyter notebooks.
We will focus our software development on the analysis and extension of biological disease knowledge networks.
PyUniProt is an ongoing project and needs improvement. We are happy if you want support our project or start
a scientific cooperation with us.


.. figure:: _static/models/all.png
   :target: _images/all.png
   :alt: ER model of PyUniProt database

**Fig. 1**: ER model of PyUniProt database

- supported by `IMI <https://www.imi.europa.eu/>`_, `AETIONOMY <http://www.aetionomy.eu/>`_, `PHAGO <https://www.imi.europa.eu/content/phago>`_.

.. image:: _static/logos/imi-logo.png
   :width: 150 px
   :target: pageapplet/index.html

.. image:: _static/logos/aetionomy-logo.png
   :width: 150 px
   :target: pageapplet/index.html

.. image:: _static/logos/scai-logo.svg
   :width: 150 px
   :target: pageapplet/index.html

.. toctree::
   :numbered:
   :maxdepth: 2

   installation
   quick_start
   tutorial
   query_functions
   restful_api
   uniprot
   benchmarks

.. toctree::
   :caption: Reference
   :name: reference

   query
   models

.. toctree::
   :numbered:
   :caption: Project
   :name: project

   roadmap
   technology

Acknowledgment and contribution to scientific projects
------------------------------------------------------

*Software development by:*

* `Christian Ebeling <https://www.scai.fraunhofer.de/de/ueber-uns/mitarbeiter/ebeling.html>`_

The software development of PyUniProt by Fraunhofer Institute for Algorithms and Scientific Computing (SCAI) is supported
and funded by the `IMI <https://www.imi.europa.eu/>`_
(INNOVATIVE MEDICINES INITIATIVE) projects `AETIONOMY <http://www.aetionomy.eu/>`_  and
`PHAGO <https://www.imi.europa.eu/content/phago>`_. The aim of both projects is the identification of mechnisms in
Alzhiemer's and Parkinson's disease in complex biological `BEL <http://openbel.org/>`_ networks for drug development.



Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`