# -*- coding: utf-8 -*-
"""SQLAlchemy database models in this module describes all tables the database.

More information how to declare models go to
http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/basic_use.html

Oberview

.. image:: _static/models/all.png
    :target: _images/all.png
"""
import inspect

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from .defaults import TABLE_PREFIX

from datetime import datetime

Base = declarative_base()


def to_dict_old(inst):
    """
    Converts a SQLAlchemy model instance in a dictionary
    """
    convert = dict()
    my_dict = dict()
    for column in inst.__class__.__table__.columns:
        value = getattr(inst, column.name)
        if column.type in convert.keys():
            try:
                my_dict[column.name] = convert[column.type](value)
            except:
                my_dict[column.name] = "Error:  Failed to covert using ", str(convert[column.type])
        else:
            my_dict[column.name] = value
    return my_dict


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        return instance


def foreign_key_to(table_name):
    """Creates a standard foreign key to a table in the database
    
    :param table_name: name of the table without TABLE_PREFIX
    :type table_name: str
    :return: foreign key column 
    :rtype: sqlalchemy.Column
    """
    foreign_column = TABLE_PREFIX + table_name + '.id'
    return Column(Integer, ForeignKey(foreign_column))


def get_many2many_table(table1, table2):
    table_name = ('{}{}__{}'.format(TABLE_PREFIX, table1, table2))
    return Table(table_name, Base.metadata,
                 Column('{}_id'.format(table1), Integer, ForeignKey('{}{}.id'.format(TABLE_PREFIX, table1))),
                 Column('{}_id'.format(table2), Integer, ForeignKey('{}{}.id'.format(TABLE_PREFIX, table2)))
                 )


class MasterModel(object):

    @declared_attr
    def __tablename__(self):
        return TABLE_PREFIX + self.__name__.lower()

    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, primary_key=True)

    def to_json(self):
        data_dict = self.__dict__.copy()
        del data_dict['_sa_instance_state']
        return data_dict

entry_pmid = get_many2many_table('entry', 'pmid')

entry_keyword = get_many2many_table('entry', 'keyword')

entry_subcellular_location = get_many2many_table('entry', 'subcellularlocation')

entry_tissue_in_reference = get_many2many_table('entry', 'tissueinreference')


class Entry(Base, MasterModel):
    """UniProt entry with relations to other models

    Query :class:`.Entry` with :func:`pyuniprot.manager.query.QueryManager.entry`

    :cvar str dataset: dataset type (SwissProt or TrEMBL)
    :cvar datetime.datetime created: Date created
    :cvar datetime.datetime modified: Datemodified
    :cvar int version: Dataset version
    :cvar str name: UniProt entry name
    :cvar str recommended_full_name: Recommended full protein name
    :cvar str recommended_short_name: Recommended short protein name
    :cvar int taxid: NCBI taxonomy identifier
    :cvar str gene_name: Primary gene name

    :cvar sequence: 1:1 to :class:`Sequence`

    :cvar collections.Iterable accessions: 1:n to :class:`.Accession`
    :cvar collections.Iterable organism_hosts: 1:n to :class:`.OrganismHost`
    :cvar collections.Iterable features: 1:n to :class:`.Feature`
    :cvar collections.Iterable functions: 1:n to :class:`.Function`
    :cvar collections.Iterable ec_numbers: 1:n to :class:`.ECNumber`
    :cvar collections.Iterable db_references: 1:n to :class:`.DbReference`
    :cvar collections.Iterable alternative_full_names: 1:n to :class:`.AlternativeFullName`
    :cvar collections.Iterable alternative_short_names: 1:n to :class:`.AlternativeShortName`
    :cvar collections.Iterable disease_comments: 1:n to :class:`.DiseaseComment`
    :cvar collections.Iterable tissue_specificities: 1:n to :class:`.TissueSpecificity`
    :cvar collections.Iterable other_gene_names: 1:n to :class:`.OtherGeneName`

    :cvar collections.Iterable pmids: n:m to :class:`.Pmid`
    :cvar collections.Iterable keywords: n:m to :class:`.Keyword`
    :cvar collections.Iterable subcellular_locations: n:m to :class:`.SubcellularLocation`
    :cvar collections.Iterable tissue_in_references: n:m to :class:`.TissueInReference`


    **Table view**

        .. image:: _static/models/sequence.png
            :target: _images/entry.png

    **Links**

    For more information on UniProt website:

    - `UniProt entry name <http://www.uniprot.org/help/entry_name>`_
    - `UniProt protein names <http://www.uniprot.org/help/protein_names>`_
    - `NCBI taxonomy identifier <http://www.uniprot.org/help/taxonomic_identifier>`_
    - `UniProt accession number <http://www.uniprot.org/help/accession_numbers>`_
    - `UniProt Sequence annotations <http://www.uniprot.org/help/sequence_annotation>`_
    - `UniProt functions <http://www.uniprot.org/help/function>`_
    - `UniProt catalytic activity <http://www.uniprot.org/help/catalytic_activity>`_
    """
    dataset = Column(String(255))
    created = Column(Date)
    modified = Column(Date)
    version = Column(Integer)
    name = Column(String(255))
    recommended_full_name = Column(Text)
    recommended_short_name = Column(Text)
    taxid = Column(Integer)
    gene_name = Column(String(255))
    sequence = relationship("Sequence", uselist=False, back_populates="entry")
    accessions = relationship("Accession", back_populates="entry")
    organism_hosts = relationship("OrganismHost", back_populates="entry")
    features = relationship("Feature", back_populates="entry")
    functions = relationship("Function", back_populates="entry")
    ec_numbers = relationship("ECNumber", back_populates="entry")
    db_references = relationship("DbReference", back_populates="entry")
    alternative_full_names = relationship("AlternativeFullName", back_populates="entry")
    alternative_short_names = relationship("AlternativeShortName", back_populates="entry")
    disease_comments = relationship("DiseaseComment", back_populates="entry")
    tissue_specificities = relationship("TissueSpecificity", back_populates="entry")
    other_gene_names = relationship("OtherGeneName", back_populates="entry")

    pmids = relationship(
        "Pmid",
        secondary=entry_pmid,
        back_populates="entries")

    keywords = relationship(
        "Keyword",
        secondary=entry_keyword,
        back_populates="entries")

    subcellular_locations = relationship(
        "SubcellularLocation",
        secondary=entry_subcellular_location,
        back_populates="entries")

    tissue_in_references = relationship(
        "TissueInReference",
        secondary=entry_tissue_in_reference,
        back_populates="entries")

    def __repr__(self):
        return self.recommended_full_name

    @property
    def data(self):
        diseases = []

        for disease_comment in self.disease_comments:
            disease_dict = {'disease_comment.comment': disease_comment.comment}

            if disease_comment.disease:
                disease_dict.update({
                    'disease.name': disease_comment.disease.name,
                    'disease.identifier': disease_comment.disease.identifier
                })
            diseases.append(disease_dict)

        data = {
            'dataset': self.dataset,
            'created': self.created,
            'modified': self.modified,
            'version': self.version,
            'name': self.name,
            'recommended_full_name': self.recommended_full_name,
            'recommended_short_name': self.recommended_short_name,
            'taxid': self.taxid,
            'gene_name': self.gene_name,
            'sequence': self.sequence,
            'accessions': [x.accession for x in self.accessions],
            'organism_hosts': [x.taxid for x in self.organism_hosts],
            'features': [(x.type_, x.identifier, x. description) for x in self.features],
            'functions': [x.text for x in self.functions],
            'ec_numbers': [x.ec_number for x in self.ec_numbers],
            'db_references': [(x.type_, x.identifier) for x in self.db_references],
            'alternative_full_names': [x.name for x in self.alternative_full_names],
            'alternative_short_names': [x.name for x in self.alternative_full_names],
            'diseases': diseases,
            'tissue_specificities': self.tissue_specificities,
            'tissue_in_references': self.tissue_in_references,
            #'other_gene_names': self.other_gene_names,
            #'pmids': self.pmids,
            #'keywords': self.keywords,
            #'subcellular_locations': self.subcellular_locations,
            #'tissue_in_references': self.tissue_in_references
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.name


class OtherGeneName(Base, MasterModel):
    """All gene names which are not primary

    Query :class:`.Entry` with :func:`pyuniprot.manager.query.QueryManager.other_gene_names`

    :cvar str type\_: type of gene name e.g. *synonym*
    :cvar str name: gene name
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/other_gene_name.png
        :target: _images/other_gene_name.png

    **Links**

        For more information on UniProt website:

        - `UniProt protein names <http://www.uniprot.org/help/protein_names>`_
    """
    type_ = Column(String(255))
    name = Column(String(255))

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="other_gene_names")

    @property
    def data(self):
        data = {
            'type': self.type_,
            'name': self.name,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return "{}: {}".format(self.type_, self.name)


class Sequence(Base, MasterModel):
    """Amino acid sequence

    :cvar str sequence: Amino acid sequence
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/sequence.png
        :target: _images/sequence.png

    **Links**

    For more information on UniProt website:

    - `UniProt sequence <hhttp://www.uniprot.org/help/sequences>`_
    """
    sequence = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="sequence")

    @property
    def data(self):
        data = {
            'sequence': self.sequence,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.sequence


class Version(Base, MasterModel):
    """Version information about UniProt knowledgebase

    :cvar str knowledgebase_type: Swiss-Prot or TrEMBL
    :cvar datetime release_date: date of release
    """
    @property
    def data(self):
        data = self.__dict__.copy()
        del data
        return data

    knowledgebase = Column(String(255), unique=True)
    release_name = Column(String(255))
    release_date = Column(Date)
    import_start_date = Column(DateTime)
    import_completed_date = Column(DateTime)

    def __repr__(self):
        return "{}:{}:{}".format(self.knowledgebase, self.release_name,  self.release_date.strftime('%Y-%m-%d'))


class Disease(Base, MasterModel):
    """Disease

    :cvar str identifier: Disease identifier
    :cvar str ref_id: Disease reference identifier
    :cvar str ref_type: Disease reference type
    :cvar str name: Disease name
    :cvar str acronym: Disease acronym
    :cvar str description: Disease description
    :cvar str disease_comments: 1:n to :class:`.DiseaseComment`


    **Table view**

    .. image:: _static/models/disease.png
        :target: _images/disease.png
    """
    identifier = Column(String(255), unique=True)
    ref_id = Column(String(255))
    ref_type = Column(String(255))
    name = Column(Text)
    acronym = Column(String(255))
    description = Column(Text)

    disease_comments = relationship("DiseaseComment", back_populates="disease")

    @property
    def entries(self):
        entry_set = set()
        for disease_comment in self.disease_comments:
            entry_set |= set([disease_comment.entry])
        return list(entry_set)

    @property
    def data(self):
        entry_db_ids = []
        for disease_comment in self.disease_comments:
            entry_db_ids.append(disease_comment.entry.id)
        data = {
            'identifier': self.identifier,
            'ref_id': self.ref_id,
            'ref_type': self.ref_type,
            'name': self.name,
            'acronym': self.acronym,
            'description': self.description,
            'entry_db_ids': entry_db_ids
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.name


class DiseaseComment(Base, MasterModel):
    """Disease and comment linked to an entry (protein)

    :cvar str comment: Comment on disease linked to a specific entry
    :cvar `Disease` disease: :class:`Disease` object
    :cvar `Entry` entry: :class:`.Entry` object

    """
    comment = Column(Text)

    disease_id = foreign_key_to('disease')
    disease = relationship("Disease", back_populates="disease_comments")

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="disease_comments")

    @property
    def data(self):
        data = {
            'comment': self.comment,
            'disease_name': (self.disease.name if self.disease else None),
            'disease_identifier': (self.disease.identifier if self.disease else None),
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.comment


class AlternativeFullName(Base, MasterModel):
    """Alternative full name

    :cvar str name: Alternative full name
    :cvar `Entry` entry: :class:`.Entry`

    **Table view**

    .. image:: _static/models/alternative_full_name.png
        :target: _images/alternative_full_names.png

    **Links**

    More information about alternative names on
    `UniProt help about 'Protein names' <http://www.uniprot.org/help/protein_names>`_
    """
    name = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="alternative_full_names")

    @property
    def data(self):
        data = {
            'name': self.name,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.name


class AlternativeShortName(Base, MasterModel):
    """Alternative short name

    :cvar str name: Alternative short name
    :cvar `Entry` entry: :class:`.Entry`

    **Table view**

    .. image:: _static/models/alternative_short_name.png
        :target: _images/alternative_short_name.png

    **Links**

    More information about alternative names on
    `UniProt help about 'Protein names' <http://www.uniprot.org/help/protein_names>`_
    """

    name = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="alternative_short_names")

    @property
    def data(self):
        data = {
            'name': self.name,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.name


class Accession(Base, MasterModel):
    """Provides a stable way of identifying UniProtKB entries.

    :cvar str accession: Accession number
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/accession.png
        :target: _images/accession.png

    **Links**

    More information about alternative names on
    `UniProt help about 'Accession' <http://www.uniprot.org/help/accession_numbers>`_

    """

    accession = Column(String(255))

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="accessions")

    @property
    def data(self):
        data = {
            'accession': self.accession,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.accession


class Pmid(Base, MasterModel):
    """PMID - The unique identifier assigned to a record when it enters PubMed.

    :cvar str pmid: PubMed identifier
    :cvar str first: first page of publication
    :cvar str last: last page of publication
    :cvar int volume: Volume
    :cvar str name: Name of Journal
    :cvar datetime.datetime date: Publication date
    :cvar str title: Title of publication


    **Table view**

    .. image:: _static/models/pmid.png
        :target: _images/pmid.png

    **Links**

    - `UniProt publications_section <http://www.uniprot.org/help/publications_section>`_
    - `PubMed web site of the National Center for Biotechnology Information <https://www.ncbi.nlm.nih.gov/pubmed/>`_
    """
    pmid = Column(Integer)
    last = Column(String(255))
    first = Column(String(255))
    volume = Column(Integer)
    name = Column(String(255))
    date = Column(Integer)
    title = Column(Text)

    entries = relationship(
        "Entry",
        secondary=entry_pmid,
        back_populates="pmids")

    @property
    def data(self):

        data = {
            'pmid': self.pmid,
            'last': self.last,
            'first': self.first,
            'volume': self.volume,
            'name': self.name,
            'date': self.date,
            'title': self.title,
            'entry_names': [x.name for x in self.entries]
        }

        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return '{}:{}'.format(self.pmid, self.title)


class OrganismHost(Base, MasterModel):
    """NCBI taxonomy database identifier of the organism host

    :cvar int taxid: NCBI Taxonomy identifier
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/organism_host.png
        :target: _images/organism_host.png

    **Links**

    - `NCBI taxonomy website <https://www.ncbi.nlm.nih.gov/taxonomy>`_
    -
    """
    taxid = Column(Integer)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="organism_hosts")

    @property
    def data(self):
        data = {
            'taxid': self.taxid,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.taxid


class DbReference(Base, MasterModel):
    """Cross reference to other databases and information resources

    :cvar str type\_: Type of cross reference
    :cvar str identifier: Unique identifier of cross reference
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/db_reference.png
        :target: _images/db_reference.png

    **Links**

    - `UniProt cross references <http://www.uniprot.org/help/cross_references_section>`_

    """
    type_ = Column(String(255))
    identifier = Column(String(255), index=True)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="db_references")

    @property
    def data(self):
        data = {
            'type': self.type_,
            'identifier': self.identifier,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return '{}:{}'.format(self.type_, self.identifier)


class Feature(Base, MasterModel):
    """Sequence annotations describe regions or sites of interest in the protein sequence, such as post-translational
    modifications, binding sites, enzyme active sites, local secondary structure or other characteristics reported
    in the cited references. In the moment we don't save the positions. If this is strongly neede contact the
    PyUniProt team on github.

    :cvar str type\_: Type of feature
    :cvar str identifier: Feature identifier
    :cvar str description: Feature description
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/feature.png
        :target: _images/feature.png

    **Links**

    - `UniProt sequence annotation (Features) <http://www.uniprot.org/help/sequence_annotation>`_
    """
    type_ = Column(String(255))
    identifier = Column(String(255))
    description = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="features")

    @property
    def data(self):
        data = {
            'type': self.type_,
            'identifier': self.identifier,
            'description': self.description,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return '{}:{} => {}'.format(self.type_, self.identifier, self.description)


class Function(Base, MasterModel):
    """General description of the function(s) of a protein

    :cvar str text: Decription of function
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/function.png
        :target: _images/function.png

    **Links**

    - `UniProt functions <http://www.uniprot.org/help/function>`_
    """
    text = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="functions")

    @property
    def data(self):
        data = {
            'text': self.text,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.text


class Keyword(Base, MasterModel):
    """UniProt keywords summarise the content of a UniProtKB entry and facilitate the search for
    proteins of interest.

    :cvar str name: Keyword
    :cvar str identifier: Keyword identifier
    :cvar list entries: list of :class:`.Entry` object

    **Table view**

    .. image:: _static/models/keyword.png
        :target: _images/keyword.png

    **Links**

    - `UniProt keywords <http://www.uniprot.org/help/keywords>`_
    """
    name = Column(Text)
    identifier = Column(String(255))

    entries = relationship(
        "Entry",
        secondary=entry_keyword,
        back_populates="keywords")

    @property
    def data(self):
        data = {
            'name': self.name,
            'identifier': self.identifier,
            'entry_names': [x.name for x in self.entries]
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return '{}:{}'.format(self.name, self.identifier)


class ECNumber(Base, MasterModel):
    """Enzyme Commission number (EC number) is a classification system for enzymes

    :cvar str ec_number: EC number
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/ec_number.png
        :target: _images/ec_number.png

    **Links**

    - `UniProt protein names <http://www.uniprot.org/help/protein_names>`_
    """
    ec_number = Column(String(255))

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="ec_numbers")

    @property
    def data(self):
        data = {
            'ec_number': self.ec_number,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.ec_number


class SubcellularLocation(Base, MasterModel):
    """Subcellular location of protein

    :cvar str location: Subcellular location
    :cvar list entries: list of :class:`.Entry` object

    **Table view**

    .. image:: _static/models/subcellular_location.png
        :target: _images/subcellular_location.png

    **Links**

    - `UniProt subcellular location <http://www.uniprot.org/help/subcellular_location>`_
    """

    location = Column(String(255), unique=True)

    entries = relationship(
        "Entry",
        secondary=entry_subcellular_location,
        back_populates="subcellular_locations")

    @property
    def data(self):
        data = {
            'location': self.location,
            'entry_names': [x.name for x in self.entries]
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.location


class TissueSpecificity(Base, MasterModel):
    """Description of the expression of a gene in different tissues

    :cvar str comment: Tissue specificity
    :cvar `Entry` entry: :class:`.Entry` object

    **Table view**

    .. image:: _static/models/tissue_specificity.png
        :target: _images/tissue_specificity.png

    **Links**

    - `UniProt tissue specificity <http://www.uniprot.org/help/tissue_specificity>`_
    """

    comment = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="tissue_specificities")

    @property
    def data(self):
        data = {
            'comment': self.comment,
            'entry_name': self.entry.name
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.comment


class TissueInReference(Base, MasterModel):
    """Tissue described in the reference

    :cvar list entries: list of :class:`.Entry` object

    **Table view**

    """
    tissue = Column(String(255), unique=True)

    entries = relationship(
        "Entry",
        secondary=entry_tissue_in_reference,
        back_populates="tissue_in_references")

    @property
    def data(self):
        data = {
            'tissue': self.tissue,
            'entry_names': [x.name for x in self.entries]
        }
        return data

    def to_json(self):
        return self.data

    def __repr__(self):
        return self.tissue


class AppUser(Base, MasterModel):
    name = Column(String(255))
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))

    def __repr__(self):
        return self.username
