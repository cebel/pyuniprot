"""Create UML models for all SQLAlchemy models in PyUniProt. Test only on Linux
install before
python3 -m pip install sadisplay
sudo apt-get install graphviz
"""

import codecs
import sadisplay
from pyuniprot.manager.database import models
import os
import sqlalchemy
import inspect

base_folder = './source/_static/models/'


def create_uml_files(list_of_models, file_prefix):
    desc = sadisplay.describe(list_of_models)
    path_prefix = os.path.join(base_folder, file_prefix)
    with codecs.open(path_prefix+'.dot', 'w', encoding='utf-8') as f:
        f.write(sadisplay.dot(desc))
    os.system(''.join(['dot -Tpng ', path_prefix, '.dot > ', path_prefix, '.png']))

# for all models one UML
list_of_all_models = [getattr(models, attr) for attr in dir(models)]
create_uml_files(list_of_all_models, 'all')


# for every model one UML
# for cls in list_of_all_models:
#     if inspect.isclass(cls) and type(cls) == sqlalchemy.ext.declarative.api.DeclarativeMeta:
#         print(cls.__name__)
#         create_uml_files([cls], cls.__name__)
#
# Special UMLs

# Entry
create_uml_files([
    models.Entry,
], 'entry')

# Sequence
create_uml_files([
    models.Sequence,
    models.Entry,
], 'sequence')

# Disease
create_uml_files([
    models.Disease,
    models .DiseaseComment,
    models.Entry,
], 'disease')

# AlternativeFullName
create_uml_files([
    models.AlternativeFullName,
    models.Entry,
], 'alternative_full_name')

# AlternativeShortName
create_uml_files([
    models.AlternativeShortName,
    models.Entry,
], 'alternative_short_name')

# Accession
create_uml_files([
    models.Accession,
    models.Entry,
], 'accession')

# Pmid
create_uml_files([
    models.Entry,
    models.Pmid,
], 'pmid')

# OrganismHost
create_uml_files([
    models.OrganismHost,
    models.Entry,
], 'organism_host')

# DbReference
create_uml_files([
    models.DbReference,
    models.Entry,
], 'db_reference')

# Feature
create_uml_files([
    models.Feature,
    models.Entry,
], 'feature')

# Function
create_uml_files([
    models.Function,
    models.Entry,
], 'function')

# Keyword
create_uml_files([
    models.Keyword,
], 'keyword')

# ECNumber
create_uml_files([
    models.ECNumber,
    models.Entry,
], 'ec_number')

# SubcellularLocation
create_uml_files([
    models.SubcellularLocation,
    models.Entry,
], 'subcellular_location')

# TissueSpecificity
create_uml_files([
    models.TissueSpecificity,
    models.Entry,
], 'tissue_specificity')

# TissueInReference
create_uml_files([
    models.TissueInReference,
    models.Entry,
], 'tissue_in_reference')

# OtherGeneName
create_uml_files([
    models.OtherGeneName,
    models.Entry,
], 'other_gene_name')