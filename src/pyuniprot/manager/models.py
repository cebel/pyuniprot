# -*- coding: utf-8 -*-
"""SQLAlchemy database models in this module describes all tables the database and 
fits the description in the table_conf module

.. image:: _static/models/all.png
    :target: _images/all.png

You find a quiet good documentation of fields at http://web.expasy.org/docs/userman.html
"""
import inspect

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date, Table
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from .defaults import TABLE_PREFIX

Base = declarative_base()


def to_dict(inst):
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
    def __tablename__(cls):
        return TABLE_PREFIX + cls.__name__.lower()

    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, primary_key=True)

    def to_json(self):
        return to_dict(self)

entry_pmid = get_many2many_table('entry', 'pmid')

entry_keyword = get_many2many_table('entry', 'keyword')

entry_subcellular_location = get_many2many_table('entry', 'subcellularlocation')

entry_tissue_in_reference = get_many2many_table('entry', 'tissueinreference')


class Entry(Base, MasterModel):
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


class Sequence(Base, MasterModel):
    sequence = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="sequence")


class Disease(Base, MasterModel):
    identifier = Column(String(255), unique=True)
    ref_id = Column(String(255))
    ref_type = Column(String(255))
    name = Column(Text)
    acronym = Column(String(255))
    description = Column(Text)

    disease_comments = relationship("DiseaseComment", back_populates="disease")

    def __repr__(self):
        return self.name


class DiseaseComment(Base, MasterModel):
    comment = Column(Text)

    disease_id = foreign_key_to('disease')
    disease = relationship("Disease", back_populates="disease_comments")

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="disease_comments")

    def __repr__(self):
        return self.comment


class AlternativeFullName(Base, MasterModel):
    name = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="alternative_full_names")

    def __repr__(self):
        return self.name


class AlternativeShortName(Base, MasterModel):
    name = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="alternative_short_names")

    def __repr__(self):
        return self.name


class Accession(Base, MasterModel):
    accession = Column(String(255))

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="accessions")

    def __repr__(self):
        return self.accession


class Pmid(Base, MasterModel):
    pmid = Column(Integer)
    last = Column(String(255))
    first = Column(String(255))
    volume = Column(Integer)
    name = Column(String(255))
    date = Column(Integer)
    type = Column(String(255))
    title = Column(Text)

    entries = relationship(
        "Entry",
        secondary=entry_pmid,
        back_populates="pmids")

    def __repr__(self):
        return '{}:{}'.format(self.pmid, self.title)


class OrganismHost(Base, MasterModel):
    taxid = Column(Integer)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="organism_hosts")

    def __repr__(self):
        return self.taxid


class DbReference(Base, MasterModel):
    type = Column(String(255))
    identifier = Column(String(255))

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="db_references")

    def __repr__(self):
        return '{}:{}'.format(self.type, self.identifier)


class Feature(Base, MasterModel):
    type = Column(String(255))
    identifier = Column(String(255))
    description = Column(String(255))

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="features")

    def __repr__(self):
        return '{}:{} => {}'.format(self.type, self.identifier, self.description)


class Function(Base, MasterModel):
    text = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="functions")

    def __repr__(self):
        return self.text


class Keyword(Base, MasterModel):
    name = Column(Text)
    identifier = Column(String(255))

    entries = relationship(
        "Entry",
        secondary=entry_keyword,
        back_populates="keywords")

    def __repr__(self):
        return '{}:{}'.format(self.name, self.identifier)


class ECNumber(Base, MasterModel):
    ec_number = Column(String(255))

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="ec_numbers")

    def __repr__(self):
        return self.ec_number


class SubcellularLocation(Base, MasterModel):
    location = Column(String(255), unique=True)

    entries = relationship(
        "Entry",
        secondary=entry_subcellular_location,
        back_populates="subcellular_locations")

    def __repr__(self):
        return self.location


class TissueSpecificity(Base, MasterModel):
    comment = Column(Text)

    entry_id = foreign_key_to('entry')
    entry = relationship("Entry", back_populates="tissue_specificities")

    def __repr__(self):
        return self.comment


class TissueInReference(Base, MasterModel):
    tissue = Column(String(255), unique=True)

    entries = relationship(
        "Entry",
        secondary=entry_tissue_in_reference,
        back_populates="tissue_in_references")

    def __repr__(self):
        return self.tissue


class AppUser(Base, MasterModel):
    name = Column(String(255))
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))

    def __repr__(self):
        return self.username
