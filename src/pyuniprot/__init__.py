"""

PyUniProt is tested on both Python2.7 and Python3

.. warning:: PyCTD is not thoroughly tested on Windows.

Installation
------------

.. code-block:: bash

    pip install pyuniprot
"""

from . import manager
from .manager.database import update, export_obo
from .manager.database import set_connection, set_mysql_connection

query = manager.query.QueryManager

__all__ = ['update', 'export_obo', 'query', 'set_connection', 'set_mysql_connection']

__version__ = '0.0.3'

__title__ = 'PyUniProt'
__description__ = 'Importing and querying UniProt'
__url__ = 'https://github.com/cebel/pyuniprot'

__author__ = 'Christian Ebeling'
__email__ = 'christian.ebeling@scai.fraunhofer.de'

__license__ = 'Apache 2.0 License'
__copyright__ = 'Copyright (c) 2017 Christian Ebeling, Fraunhofer Institute for Algorithms and Scientific Computing ' \
                'SCAI, Schloss Birlinghoven, 53754 Sankt Augustin, Germany'
