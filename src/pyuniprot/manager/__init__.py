"""
The pyuniprot.manager module serves as an interface between the UniProt data structure and underlying relational
databases.
"""
from . import defaults
from . import models
from . import database
from . import query

from . import make_json_serializable
