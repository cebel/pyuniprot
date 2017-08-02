# -*- coding: utf-8 -*-
"""PyCTD loads all CTD content in the database. Content is available via functions."""
import logging
import os
import sys
import gzip
import configparser
import time

import numpy as np

from datetime import datetime
from pathlib import Path
from lxml import etree
from configparser import RawConfigParser
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import reflection
from sqlalchemy.sql import sqltypes

from . import defaults
from . import models
from ..constants import bcolors
from ..constants import PYUNIPROT_DATA_DIR, PYUNIPROT_DIR


if sys.version_info[0] == 3:
    from urllib.request import urlretrieve
    from requests.compat import urlparse
else:
    from urllib import urlretrieve
    from urlparse import urlparse

log = logging.getLogger(__name__)

alchemy_pandas_dytpe_mapper = {
    sqltypes.Text: np.unicode,
    sqltypes.String: np.unicode,
    sqltypes.Integer: np.float,
    sqltypes.REAL: np.double
}


def get_connection_string(connection=None):
    """return SQLAlchemy connection string if it is set

    :param connection: get the SQLAlchemy connection string #TODO
    :rtype: str
    """
    if not connection:
        config = configparser.ConfigParser()
        cfp = defaults.config_file_path
        if os.path.exists(cfp):
            log.info('fetch database configuration from %s', cfp)
            config.read(cfp)
            connection = config['database']['sqlalchemy_connection_string']
            log.info('load connection string from %s: %s', cfp, connection)
        else:
            with open(cfp, 'w') as config_file:
                connection = defaults.sqlalchemy_connection_string_default
                config['database'] = {'sqlalchemy_connection_string': connection}
                config.write(config_file)
                log.info('create configuration file %s', cfp)

    return connection


def gunzip_file(path):
    """gunzip path and returns path to extracted file

    :param str path: path to gzip file
    :return: path to extracted file
    :rtype: pathlib.Path
    """

    gzipped_path = Path(path)
    extracted_path = Path(path[:-3])

    if not extracted_path.exists() and gzipped_path.is_file() and gzipped_path.suffix == '.gz':
        with gzip.open(str(gzipped_path), 'rb') as gzipped_file, extracted_path.open('wb') as extracted_file:
            extracted_file.write(gzipped_file.read())

    if extracted_path.is_file():
        return extracted_path
    else:
        return None


class BaseDbManager(object):
    """Creates a connection to database and a persistient session using SQLAlchemy"""

    def __init__(self, connection=None, echo=False):
        """
        :param str connection: SQLAlchemy 
        :param bool echo: True or False for SQL output of SQLAlchemy engine
        """
        log.setLevel(logging.INFO)
        
        handler = logging.FileHandler(os.path.join(PYUNIPROT_DIR, defaults.TABLE_PREFIX + 'database.log'))
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)

        try:
            self.connection = get_connection_string(connection)
            self.engine = create_engine(self.connection, echo=echo)
            self.inspector = reflection.Inspector.from_engine(self.engine)
            self.sessionmaker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
            self.session = scoped_session(self.sessionmaker)()
        except:
            self.set_connection_string_by_user_input()
            self.__init__()

    def set_connection_string_by_user_input(self):
        """If no connection is available request of connection string by user"""
        user_connection = input(
            bcolors.WARNING + "\nFor any reason connection to " + bcolors.ENDC +
            bcolors.FAIL + "{}".format(self.connection) + bcolors.ENDC +
            bcolors.WARNING + " is not possible.\n\n" + bcolors.ENDC +
            "For more information about SQLAlchemy connection strings go to:\n" +
            "http://docs.sqlalchemy.org/en/latest/core/engines.html\n\n"
            "Please insert a valid connection string:\n" +
            bcolors.UNDERLINE + "Examples:\n\n" + bcolors.ENDC +
            "MySQL (recommended):\n" +
            bcolors.OKGREEN + "\tmysql+pymysql://user:passwd@localhost/database?charset=utf8\n" + bcolors.ENDC +
            "PostgreSQL:\n" +
            bcolors.OKGREEN + "\tpostgresql://scott:tiger@localhost/mydatabase\n" + bcolors.ENDC +
            "MsSQL (pyodbc have to be installed):\n" +
            bcolors.OKGREEN + "\tmssql+pyodbc://user:passwd@database\n" + bcolors.ENDC +
            "SQLite (always works):\n" +
            " - Linux:\n" +
            bcolors.OKGREEN + "\tsqlite:////absolute/path/to/database.db\n" + bcolors.ENDC +
            " - Windows:\n" +
            bcolors.OKGREEN + "\tsqlite:///C:\\path\\to\\database.db\n" + bcolors.ENDC +
            "Oracle:\n" +
            bcolors.OKGREEN + "\toracle://user:passwd@127.0.0.1:1521/database\n\n" + bcolors.ENDC +
            "[RETURN] for standard connection {}:\n".format(defaults.sqlalchemy_connection_string_default)
        )
        if not (user_connection or user_connection.strip()):
            user_connection = defaults.sqlalchemy_connection_string_default
        set_connection(user_connection.strip())

    def _create_tables(self, checkfirst=True):
        """creates all tables from models in your database
        
        :param checkfirst: True or False check if tables already exists
        :type checkfirst: bool
        :return: 
        """
        log.info('create tables in {}'.format(self.engine.url))
        models.Base.metadata.create_all(self.engine, checkfirst=checkfirst)

    def _drop_tables(self):
        """drops all tables in the database"""
        log.info('drop tables in {}'.format(self.engine.url))
        self.session.commit()
        models.Base.metadata.drop_all(self.engine)
        self.session.commit()


class DbManager(BaseDbManager):
    pyuniprot_data_dir = PYUNIPROT_DATA_DIR
    organism_hosts = {}
    pmids = {}
    accessions = {}
    keywords = {}
    subcellular_locations = {}
    tissues = {}

    def __init__(self, connection=None):
        """The DbManager implements all function to upload CTD files into the database. Prefered SQL Alchemy 
        database is MySQL with pymysql.
        
        :param connection: custom database connection SQL Alchemy string
        :type connection: str
        """
        super(DbManager, self).__init__(connection=connection)

    def db_import_xml(self, url=None, force_download=False, taxids=None):
        """Updates the CTD database
        
        1. downloads gzipped XML
        2. drops all tables in database
        3. creates all tables in database
        4. import XML
        5. close session

        :param taxids: list of NCBI taxonomy identifier
        :type taxids: list
        :param url: iterable of URL strings
        :type url: str
        :param force_download: force method to download
        :type: bool
        """

        log.info('Update CTD database from {}'.format(url))

        self._drop_tables()
        xml_gzipped_file_path = DbManager.download(url, force_download)
        self._create_tables()
        self.import_xml(xml_gzipped_file_path, taxids)
        self.session.close()

    def import_xml(self, xml_gzipped_file_path, taxids):
        """Imports XML"""
        entry_xml = ['<entries>']
        number_of_entries = 0
        interval = 100
        start = False

        xml_file = gunzip_file(xml_gzipped_file_path)

        with xml_file.open('r') as fd:
            for line in fd:
                end_of_file = line.startswith("</uniprot>")
                if line.startswith("<entry "):
                    start = True
                elif end_of_file:
                    start = False
                if start:
                    entry_xml += [line]
                if line.startswith("</entry>") or end_of_file:
                    number_of_entries += 1
                    start = False

                    if number_of_entries == interval or end_of_file:
                        entry_xml += ["</entries>"]
                        self.insert_entries(entry_xml, taxids)
                        self.session.commit()
                        if end_of_file:
                            break
                        else:
                            entry_xml = ["<entries>"]
                            number_of_entries = 0

    def insert_entries(self, entries_xml, taxids):
        """insert UniProt entries from XML"""
        entries = etree.fromstringlist(entries_xml)
        for entry in entries:
            self.insert_entry(entry, taxids)

    def insert_entry(self, entry, taxids):
        """insert UniProt entry"""
        entry_dict = dict(entry.attrib)
        entry_dict['created'] = datetime.strptime(entry_dict['created'], '%Y-%m-%d')
        entry_dict['modified'] = datetime.strptime(entry_dict['modified'], '%Y-%m-%d')

        taxid = self.get_taxid(entry)

        if taxids is None or taxid in taxids:
            self.update_entry_dict(entry, entry_dict, taxid)
            entry_obj = models.Entry(**entry_dict)
            self.session.add(entry_obj)

    def update_entry_dict(self, entry, entry_dict, taxid):
        rp_full, rp_short = self.get_recommended_protein_name(entry)

        entry_dict.update(
            accessions=self.get_accessions(entry),
            sequence=self.get_sequence(entry),
            name=self.get_entry_name(entry),
            pmids=self.get_pmids(entry),
            subcellular_locations=self.get_subcellular_locations(entry),
            tissue_in_references=self.get_tissue_in_references(entry),
            organism_hosts=self.get_organism_hosts(entry),
            recommended_full_name=rp_full,
            recommended_short_name=rp_short,
            taxid=taxid,
            db_references=self.get_db_references(entry),
            features=self.get_features(entry),
            functions=self.get_functions(entry),
            gene_name=self.get_gene_name(entry),
            keywords=self.get_keywords(entry),
            ec_numbers=self.get_ec_numbers(entry),
            alternative_full_names=self.get_alternative_full_names(entry),
            alternative_short_names=self.get_alternative_short_names(entry),
            disease_comments=self.get_disease_comments(entry),
            tissue_specificities=self.get_tissue_specificities(entry)
        )
        return entry_dict

    @classmethod
    def get_sequence(cls, entry):
        seq_tag = entry.find("./sequence")
        return models.Sequence(sequence=seq_tag.text)

    def get_tissue_in_references(self, entry):
        tissue_in_references = []

        tissues = {x.text for x in entry.findall("./reference/source/tissue")}

        for tissue in tissues:

            if tissue not in self.tissues:
                self.tissues[tissue] = models.TissueInReference(tissue=tissue)
            tissue_in_references.append(self.tissues[tissue])

        return tissue_in_references

    @classmethod
    def get_tissue_specificities(cls, entry):
        tissue_specificities = []

        query = "./comment[@type='tissue specificity']/text"

        for ts in entry.findall(query):
            tissue_specificities.append(models.TissueSpecificity(comment=ts.text))

        return tissue_specificities

    def get_subcellular_locations(self, entry):
        subcellular_locations = []

        sls = {x.text for x in entry.findall('./comment/subcellularLocation/location')}

        for sl in sls:

            if sl not in self.subcellular_locations:
                self.subcellular_locations[sl] = models.SubcellularLocation(location=sl)
            subcellular_locations.append(self.subcellular_locations[sl])

        return subcellular_locations

    def get_keywords(self, entry):
        keywords = []

        for keyword in entry.findall("./keyword"):
            identifier = keyword.get('id')
            name = keyword.text
            keyword_hash = hash(identifier)

            if keyword_hash not in self.keywords:
                self.keywords[keyword_hash] = models.Keyword(**{'identifier': identifier, 'name': name})
            keywords.append(self.keywords[keyword_hash])

        return keywords

    @classmethod
    def get_entry_name(cls, entry):
        name = entry.find('./name').text
        return name

    def get_disease_comments(self, entry):
        disease_comments = []
        query = "./comment[@type='disease']"

        for disease_comment in entry.findall(query):
            value_dict = {'comment':disease_comment.find('text').text}

            disease = disease_comment.find("./disease")

            if disease is not None:
                disease_dict = {'identifier': disease.get('id')}
                for element in disease:
                    key = element.tag
                    if key in ['acronym', 'description', 'name']:
                        disease_dict[key] = element.text
                    if key == 'dbReference':
                        disease_dict['ref_id'] = element.get('id')
                        disease_dict['ref_type'] = element.get('type')
                disease_obj = models.get_or_create(self.session, models.Disease, **disease_dict)
                self.session.add(disease_obj)
                self.session.flush()
                value_dict['disease_id'] = disease_obj.id
            disease_comments.append(models.DiseaseComment(**value_dict))
        return disease_comments

    @classmethod
    def get_alternative_full_names(cls, entry):
        names = []
        query = "./protein/alternativeName/fullName"
        for name in entry.findall(query):
            names.append(models.AlternativeFullName(name=name.text))
        return names

    @classmethod
    def get_alternative_short_names(cls, entry):
        names = []
        query = "./protein/alternativeName/shortName"
        for name in entry.findall(query):
            names.append(models.AlternativeShortName(name=name.text))
        return names

    @classmethod
    def get_ec_numbers(cls, entry):
        ec_numbers = []
        query = "./protein/recommendedName/ecNumber"
        for ec in entry.findall(query):
            ec_numbers.append(models.ECNumber(ec_number=ec.text))
        return ec_numbers

    @classmethod
    def get_gene_name(cls, entry):
        gene_name = entry.find("gene/name[@type='primary']")
        return gene_name.text if isinstance(gene_name, etree._Element) else None

    @classmethod
    def get_accessions(cls, entry):
        return [models.Accession(accession=x.text) for x in entry.findall("./accession")]

    @classmethod
    def get_db_references(cls, entry):
        db_refs = []
        query = "./dbReference"
        for db_ref in entry.findall(query):
            attrib_dict = dict(db_ref.attrib)
            db_ref_dict = {'identifier':attrib_dict['id'], 'type': attrib_dict['type']}
            db_refs.append(models.DbReference(**db_ref_dict))
        return db_refs

    @classmethod
    def get_features(cls, entry):
        features = []
        for feature in entry.findall("./feature"):
            attrib_dict = dict(feature.attrib)
            feature_dict = {
                'description': attrib_dict.get('description'),
                'type': attrib_dict['type']
            }
            if 'id' in attrib_dict:
                feature_dict['identifier'] = attrib_dict.pop('id')
            features.append(models.Feature(**feature_dict))
        return features

    @classmethod
    def get_taxid(cls, entry):
        query = "./organism/dbReference[@type='NCBI Taxonomy']"
        return int(entry.find(query).get('id'))

    @classmethod
    def get_recommended_protein_name(cls, entry):
        query_full = "./protein/recommendedName/fullName"
        full_name = entry.find(query_full).text

        short_name = None
        query_short = "./protein/recommendedName/shortName"
        short_name_tag = entry.find(query_short)
        if short_name_tag is not None:
            short_name = short_name_tag.text

        return full_name, short_name

    @classmethod
    def get_organism_hosts(cls, entry):
        query = "./organismHost/dbReference[@type='NCBI Taxonomy']"
        return [models.OrganismHost(taxid=x.get('id')) for x in entry.findall(query)]

    def get_pmids(self, entry):
        pmids = []
        pmids_found = entry.findall("./reference/citation/dbReference[@type='PubMed']")
        for pmid in pmids_found:
            pmid_number = pmid.get('id')
            if pmid_number not in self.pmids:
                citation = pmid.getparent()
                pmid_dict = dict(citation.attrib)
                pmid_dict.update(pmid=pmid_number)
                title_tag = citation.find('./title')
                if title_tag is not None:
                    pmid_dict.update(title=title_tag.text)
                self.pmids[pmid_number] = models.Pmid(**pmid_dict)
            pmids.append(self.pmids[pmid_number])
        return pmids

    @classmethod
    def get_functions(cls, entry):
        comments = []
        for comment in entry.findall("./comment[@type='function']"):
            text = comment.find('./text').text
            comments.append(models.Function(text=text))
        return comments

    @classmethod
    def get_dtypes(cls, sqlalchemy_model):
        mapper = inspect(sqlalchemy_model)
        dtypes = {x.key: alchemy_pandas_dytpe_mapper[type(x.type)] for x in mapper.columns if x.key != 'id'}
        return dtypes

    @classmethod
    def download(cls, url=None, force_download=False):
        """Downloads uniprot_sprot.xml.gz from URL
    
        :param url: UniProt gzipped URL
        :type url: string
        :param force_download: force method to download
        :type force_download: bool
        """
        url = url if url else defaults.XML_SPROT_URL
        file_path = cls.get_path_to_file_from_url(url)
        if force_download or not os.path.exists(file_path):
            log.info('download {}'.format(file_path))
            urlretrieve(url, file_path)
        return file_path

    @classmethod
    def get_path_to_file_from_url(cls, url):
        """standard file path
        
        :param str url: CTD download URL 
        """
        file_name = urlparse(url).path.split('/')[-1]
        return os.path.join(cls.pyuniprot_data_dir, file_name)

    def export_obo(self, path_to_export_file, name_of_ontology="uniprot", taxids=None):
        """
        export complete database to OBO (http://www.obofoundry.org/) file

        :param path_to_export_file: path to export file
        :param taxids: NCBI taxonomy identifiers to export (optional)
        """

        fd = open(path_to_export_file, 'w')

        header = "format-version: 0.1\ndata: {}\n".format(time.strftime("%d:%m:%Y %H:%M"))
        header += "ontology: {}\n".format(name_of_ontology)
        header += 'synonymtypedef: GENE_NAME "GENE NAME"\nsynonymtypedef: ALTERNATIVE_NAME "ALTERNATIVE NAME"\n'

        fd.write(header)

        query = self.session.query(models.Entry).limit(100)

        if taxids:
            query = query.filter(models.Entry.taxid.in_(taxids))

        for entry in query.all():

            fd.write('\n[Term]\nid: SWISSPROT:{}\n'.format(entry.accessions[0]))

            if len(entry.accessions) > 1:
                for accession in entry.accessions[1:]:
                    fd.write('alt_id: {}\n'.format(accession))

            fd.write('name: {}\n'.format(entry.recommended_full_name))

            for alternative_full_name in entry.alternative_full_names:
                fd.write('synonym: "{}" EXACT ALTERNATIVE_NAME []\n'.format(alternative_full_name.name))

            for alternative_short_name in entry.alternative_short_names:
                fd.write('synonym: "{}" EXACT ALTERNATIVE_NAME []\n'.format(alternative_short_name.name))

            fd.write('synonym: "{}" EXACT GENE_NAME []\n'.format(entry.gene_name))

            for xref in entry.db_references:
                if xref.type in ['GO', 'HGNC']:
                    xref.identifier = ':'.join(xref.identifier.split(':')[1:])
                fd.write('xref: {}:{}\n'.format(xref.type, xref.identifier.replace('\\', '\\\\')))

        fd.close()


def update(connection=None, urls=None, force_download=False, taxids=None):
    """Updates CTD database

    :param urls: list of urls to download
    :type urls: iterable
    :param connection: custom database connection string
    :type connection: str
    :param force_download: force method to download
    :type force_download: bool
    :param taxids: iterable of NCBI taxonomy identifiers (default is None = load all)
    :type taxids: iterable of integers
    """

    db = DbManager(connection)
    db.db_import_xml(urls, force_download, taxids)
    db.session.close()


def set_mysql_connection(host='localhost', user='pyuniprot_user', passwd='pyuniprot_passwd', db='pyuniprot',
                         charset='utf8'):
    set_connection('mysql+pymysql://{user}:{passwd}@{host}/{db}?charset={charset}'.format(
        host=host,
        user=user,
        passwd=passwd,
        db=db,
        charset=charset)
    )


def set_test_connection():
    set_connection(defaults.DEFAULT_SQLITE_TEST_DATABASE_NAME)


def set_connection(connection=defaults.sqlalchemy_connection_string_default):
    """
    Set the connection string for sqlalchemy
    :param str connection: sqlalchemy connection string
    """
    cfp = defaults.config_file_path
    config = RawConfigParser()

    if not os.path.exists(cfp):
        with open(cfp, 'w') as config_file:
            config['database'] = {'sqlalchemy_connection_string': connection}
            config.write(config_file)
            log.info('create configuration file {}'.format(cfp))
    else:
        config.read(cfp)
        config.set('database', 'sqlalchemy_connection_string', connection)
        with open(cfp, 'w') as configfile:
            config.write(configfile)


def export_obo(path_to_file, connection=None):
    """export database to obo file

    :param path_to_file: path to export file
    :param connection: connection string (optional)
    :return:
    """
    db = DbManager(connection)
    db.export_obo(path_to_export_file=path_to_file)
    db.session.close()
