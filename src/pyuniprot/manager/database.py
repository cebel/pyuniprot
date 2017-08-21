# -*- coding: utf-8 -*-
"""PyCTD loads all CTD content in the database. Content is available via functions."""
import logging
import os
import sys
import gzip
import configparser
import time
import re
import subprocess
import shutil
import sqlalchemy

import numpy as np
import xml.etree.cElementTree as etree

from tqdm import tqdm
from datetime import datetime
from configparser import RawConfigParser

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import reflection
from sqlalchemy.sql import sqltypes

from . import defaults
from . import models
from ..constants import PYUNIPROT_DATA_DIR, PYUNIPROT_DIR


if sys.version_info[0] == 3:
    from urllib.request import urlretrieve
    from requests.compat import urlparse, urlsplit
else:
    from urllib import urlretrieve
    from urlparse import urlparse, urlsplit

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
            self.engine = sqlalchemy.create_engine(self.connection, echo=echo)

            self.inspector = reflection.Inspector.from_engine(self.engine)
            self.sessionmaker = sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=True
            )
            self.session = scoped_session(self.sessionmaker)
        except:
            log.warning('No valid database connection. Execute `pyuniprot connection` on command line')

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
    pmids = set()
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
        self.parser = None

    def db_import_xml(self, url=None, force_download=False, taxids=None, silent=False):
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
        xml_gzipped_file_path, version_file_path = self.download(url, force_download)
        self._create_tables()
        self.import_version(version_file_path)
        self.import_xml(xml_gzipped_file_path, taxids, silent)
        self.session.close()

    def import_version(self, version_file_path):
        pattern = "UniProtKB/(?P<knowledgebase>Swiss-Prot|TrEMBL) Release" \
                  " (?P<release_name>\\d{4}_\\d{2}) of (?P<release_date>\\d{2}-\\w{3}-\\d{4})"
        with open(version_file_path) as fd:
            content = fd.read()

        for knowledgebase, release_name, release_date_str in re.findall(pattern, content):
            release_date = datetime.strptime(release_date_str, '%d-%b-%Y')

            version = models.Version(
                knowledgebase=knowledgebase,
                release_name=release_name,
                release_date=release_date
            )

            self.session.add(version)

        self.session.commit()

    def import_xml(self, xml_gzipped_file_path, taxids, silent=False):
        """Imports XML

        :param str xml_gzipped_file_path: path to XML file
        :param int,(int,),[int,] taxids: NCBI taxonomy identifier
        :param bool silent: no output if True
        """
        version = self.session.query(models.Version).filter(models.Version.knowledgebase == 'Swiss-Prot').first()
        version.import_start_date = datetime.now()

        entry_xml = '<entries>'
        number_of_entries = 0
        interval = 1000
        start = False

        if sys.platform in ('linux', 'darwin'):
            log.info('Load gzipped XML from {}'.format(xml_gzipped_file_path))
            number_of_lines = int(subprocess.getoutput("zcat {} | wc -l".format(xml_gzipped_file_path)))
            tqdm_desc = 'Imported from {} lines'.format(number_of_lines)

        else:
            number_of_lines = None
            tqdm_desc = None

        with gzip.open(xml_gzipped_file_path) as fd:

            for line in tqdm(fd, desc=tqdm_desc, total=number_of_lines, mininterval=1, disable=silent):

                end_of_file = line.startswith(b"</uniprot>")

                if line.startswith(b"<entry "):
                    start = True

                elif end_of_file:
                    start = False

                if start:
                    entry_xml += line.decode("utf-8")

                if line.startswith(b"</entry>") or end_of_file:
                    number_of_entries += 1
                    start = False

                    if number_of_entries == interval or end_of_file:

                        entry_xml += "</entries>"
                        self.insert_entries(entry_xml, taxids)

                        if end_of_file:
                            break

                        else:
                            entry_xml = "<entries>"
                            number_of_entries = 0

        version.import_completed_date = datetime.now()
        self.session.commit()

    def insert_entries(self, entries_xml, taxids):
        """
        insert UniProt entries from XML

        :param str entries_xml: XML string
        :param int,tuple,list taxids: NCBI taxonomy IDs
        :return:
        """

        entries = etree.fromstring(entries_xml)
        del entries_xml

        for entry in entries:
            self.insert_entry(entry, taxids)
            entry.clear()
            del entry

        entries.clear()
        del entries

        self.session.commit()

    # profile
    def insert_entry(self, entry, taxids):
        """
        insert UniProt entry"

        :param entry: XML node entry
        :param taxids: int,tuple,list taxids: NCBI taxonomy IDs
        :return:
        """
        entry_dict = entry.attrib
        entry_dict['created'] = datetime.strptime(entry_dict['created'], '%Y-%m-%d')
        entry_dict['modified'] = datetime.strptime(entry_dict['modified'], '%Y-%m-%d')

        taxid = self.get_taxid(entry)

        if taxids is None or taxid in taxids:
            entry_dict = self.update_entry_dict(entry, entry_dict, taxid)
            entry_obj = models.Entry(**entry_dict)
            del entry_dict

            self.session.add(entry_obj)

    # @profile
    def update_entry_dict(self, entry, entry_dict, taxid):
        """

        :param entry: XML node entry
        :param entry_dict: dictionary used to initialize `models.Entry`
        :param int taxid: NCBI taxonomy ID
        :return:
        """
        rp_full, rp_short = self.get_recommended_protein_name(entry)

        pmids = self.get_pmids(entry)
        accessions = self.get_accessions(entry)
        sequence = self.get_sequence(entry)
        name = self.get_entry_name(entry)
        subcellular_locations = self.get_subcellular_locations(entry)
        tissue_in_references = self.get_tissue_in_references(entry)
        organism_hosts = self.get_organism_hosts(entry)
        db_references = self.get_db_references(entry)
        other_gene_names = self.get_other_gene_names(entry)
        features = self.get_features(entry)
        functions = self.get_functions(entry)
        gene_name = self.get_gene_name(entry)
        keywords = self.get_keywords(entry)
        ec_numbers = self.get_ec_numbers(entry)
        alternative_full_names = self.get_alternative_full_names(entry)
        alternative_short_names = self.get_alternative_short_names(entry)
        disease_comments = self.get_disease_comments(entry)
        tissue_specificities = self.get_tissue_specificities(entry)

        entry_dict.update(
            accessions=accessions,
            sequence=sequence,
            name=name,
            pmids=pmids,
            subcellular_locations=subcellular_locations,
            tissue_in_references=tissue_in_references,
            organism_hosts=organism_hosts,
            recommended_full_name=rp_full,
            recommended_short_name=rp_short,
            taxid=taxid,
            db_references=db_references,
            other_gene_names=other_gene_names,
            features=features,
            functions=functions,
            gene_name=gene_name,
            keywords=keywords,
            ec_numbers=ec_numbers,
            alternative_full_names=alternative_full_names,
            alternative_short_names=alternative_short_names,
            disease_comments=disease_comments,
            tissue_specificities=tissue_specificities
        )
        return entry_dict

    @classmethod
    def get_sequence(cls, entry):
        """
        get models.Sequence object from XML node entry

        :param entry: XML node entry
        :return: :class:`pyuniprot.manager.models.Sequence` object
        """
        seq_tag = entry.find("./sequence")
        seq = seq_tag.text
        seq_tag.clear()
        return models.Sequence(sequence=seq)

    def get_tissue_in_references(self, entry):
        """
        get list of models.TissueInReference from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.TissueInReference` objects
        """
        tissue_in_references = []
        query = "./reference/source/tissue"
        tissues = {x.text for x in entry.iterfind(query)}

        for tissue in tissues:

            if tissue not in self.tissues:
                self.tissues[tissue] = models.TissueInReference(tissue=tissue)
            tissue_in_references.append(self.tissues[tissue])

        return tissue_in_references

    @classmethod
    def get_tissue_specificities(cls, entry):
        """
        get list of :class:`pyuniprot.manager.models.TissueSpecificity` object from XML node entry

        :param entry: XML node entry
        :return: models.TissueSpecificity object
        """
        tissue_specificities = []

        query = "./comment[@type='tissue specificity']/text"

        for ts in entry.iterfind(query):
            tissue_specificities.append(models.TissueSpecificity(comment=ts.text))

        return tissue_specificities

    def get_subcellular_locations(self, entry):
        """
        get list of models.SubcellularLocation object from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.SubcellularLocation` object
        """
        subcellular_locations = []
        query = './comment/subcellularLocation/location'
        sls = {x.text for x in entry.iterfind(query)}

        for sl in sls:

            if sl not in self.subcellular_locations:
                self.subcellular_locations[sl] = models.SubcellularLocation(location=sl)
            subcellular_locations.append(self.subcellular_locations[sl])

        return subcellular_locations

    def get_keywords(self, entry):
        """
        get list of models.Keyword objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.Keyword` objects
        """
        keyword_objects = []

        for keyword in entry.iterfind("./keyword"):
            identifier = keyword.get('id')
            name = keyword.text
            keyword_hash = hash(identifier)

            if keyword_hash not in self.keywords:
                self.keywords[keyword_hash] = models.Keyword(**{'identifier': identifier, 'name': name})

            keyword_objects.append(self.keywords[keyword_hash])

        return keyword_objects

    @classmethod
    def get_entry_name(cls, entry):
        """
        get entry name as string from XML node entry

        :param entry: XML node entry
        :return: unique entry name
        """
        name = entry.find('./name').text
        return name

    def get_disease_comments(self, entry):
        """
        get list of models.Disease objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.Disease` objects
        """
        disease_comments = []
        query = "./comment[@type='disease']"

        for disease_comment in entry.iterfind(query):
            value_dict = {'comment': disease_comment.find('./text').text}

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
        """
        get list of models.AlternativeFullName objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.AlternativeFullName` objects
        """
        names = []
        query = "./protein/alternativeName/fullName"
        for name in entry.iterfind(query):
            names.append(models.AlternativeFullName(name=name.text))

        return names

    @classmethod
    def get_alternative_short_names(cls, entry):
        """
        get list of models.AlternativeShortName objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.AlternativeShortName` objects
        """
        names = []
        query = "./protein/alternativeName/shortName"
        for name in entry.iterfind(query):
            names.append(models.AlternativeShortName(name=name.text))

        return names

    @classmethod
    def get_ec_numbers(cls, entry):
        """
        get list of models.ECNumber objects from XML node entry

        :param entry:  XML node entry
        :return: list of models.ECNumber objects
        """
        ec_numbers = []

        for ec in entry.iterfind("./protein/recommendedName/ecNumber"):
            ec_numbers.append(models.ECNumber(ec_number=ec.text))
        return ec_numbers

    @classmethod
    def get_gene_name(cls, entry):
        """
        get primary gene name from XML node entry

        :param entry: XML node entry
        :return: str
        """
        gene_name = entry.find("./gene/name[@type='primary']")

        return gene_name.text if gene_name is not None and gene_name.text.strip() else None

    @classmethod
    def get_other_gene_names(cls, entry):
        """
        get list of `models.OtherGeneName` objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.models.OtherGeneName` objects
        """
        alternative_gene_names = []

        for alternative_gene_name in entry.iterfind("./gene/name"):

            if alternative_gene_name.attrib['type'] != 'primary':

                alternative_gene_name_dict = {
                    'type_': alternative_gene_name.attrib['type'],
                    'name': alternative_gene_name.text
                }

                alternative_gene_names.append(models.OtherGeneName(**alternative_gene_name_dict))

        return alternative_gene_names

    @classmethod
    def get_accessions(cls, entry):
        """
        get list of models.Accession from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.Accession` objects
        """
        return [models.Accession(accession=x.text) for x in entry.iterfind("./accession")]

    @classmethod
    def get_db_references(cls, entry):
        """
        get list of `models.DbReference` from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.DbReference`
        """
        db_refs = []

        for db_ref in entry.iterfind("./dbReference"):

            db_ref_dict = {'identifier': db_ref.attrib['id'], 'type_': db_ref.attrib['type']}
            db_refs.append(models.DbReference(**db_ref_dict))

        return db_refs

    @classmethod
    def get_query_string(cls, query):
        """
        get correct XPath string if XML namespace is ignored (not used in the current implementation)

        :param str query: query string without namespace
        :return: query string with namespace
        """
        return '/{http://uniprot.org/uniprot}'.join(query.split('/'))

    @classmethod
    def get_features(cls, entry):
        """
        get list of `models.Feature` from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.Feature`
        """
        features = []

        for feature in entry.iterfind("./feature"):

            feature_dict = {
                'description': feature.attrib.get('description'),
                'type_': feature.attrib['type'],
                'identifier': feature.attrib.get('id')
            }

            features.append(models.Feature(**feature_dict))

        return features

    @classmethod
    def get_taxid(cls, entry):
        """
        get NCBI taxonomy identifier from XML node entry

        :param entry:X ML node entry
        :return: int
        """
        query = "./organism/dbReference[@type='NCBI Taxonomy']"
        return int(entry.find(query).get('id'))

    @classmethod
    def get_recommended_protein_name(cls, entry):
        """
        get recommended full and short protein name as tuple from XML node

        :param entry: XML node entry
        :return: (str, str) => (full, short)
        """
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
        """
        get list of `models.OrganismHost` objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.OrganismHost` objects
        """

        query = "./organismHost/dbReference[@type='NCBI Taxonomy']"
        return [models.OrganismHost(taxid=x.get('id')) for x in entry.iterfind(query)]

    def get_pmids(self, entry):
        """
        get `models.Pmid` objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.Pmid` objects
        """
        pmids = []

        for citation in entry.iterfind("./reference/citation"):

            for pubmed_ref in citation.iterfind('dbReference[@type="PubMed"]'):

                pmid_number = pubmed_ref.get('id')

                if pmid_number in self.pmids:

                    pmid_sqlalchemy_obj = self.session.query(models.Pmid)\
                        .filter(models.Pmid.pmid == pmid_number).one()

                    pmids.append(pmid_sqlalchemy_obj)

                else:
                    pmid_dict = citation.attrib
                    if not re.search('^\d+$', pmid_dict['volume']):
                        pmid_dict['volume'] = -1

                    del pmid_dict['type'] # not needed because already filtered for PubMed

                    pmid_dict.update(pmid=pmid_number)
                    title_tag = citation.find('./title')

                    if title_tag is not None:
                        pmid_dict.update(title=title_tag.text)

                    pmid_sqlalchemy_obj = models.Pmid(**pmid_dict)
                    self.session.add(pmid_sqlalchemy_obj)
                    self.session.flush()

                    pmids.append(pmid_sqlalchemy_obj)

                    self.pmids |= set([pmid_number, ]) # extend the cache of identifiers

        return pmids

    @classmethod
    def get_functions(cls, entry):
        """
        get `models.Function` objects from XML node entry

        :param entry: XML node entry
        :return: list of :class:`pyuniprot.manager.models.Function` objects
        """
        comments = []
        query = "./comment[@type='function']"
        for comment in entry.iterfind(query):
            text = comment.find('./text').text
            comments.append(models.Function(text=text))

        return comments

    @classmethod
    def get_dtypes(cls, sqlalchemy_model):
        mapper = sqlalchemy.inspect(sqlalchemy_model)
        dtypes = {x.key: alchemy_pandas_dytpe_mapper[type(x.type)] for x in mapper.columns if x.key != 'id'}
        return dtypes

    @classmethod
    def download(cls, url=None, force_download=False):
        """Downloads uniprot_sprot.xml.gz and reldate.txt (release date information) from URL or file path

        .. note::

            only URL/path of xml.gz is needed and valid value for parameter url. URL/path for reldate.txt have to be the
            same folder
    
        :param str url: UniProt gzipped URL or file path
        :param force_download: force method to download
        :type force_download: bool
        """
        if url:
            version_url = os.path.join(os.path.dirname(url), defaults.VERSION_FILE_NAME)
        else:
            url = os.path.join(defaults.XML_DIR_NAME, defaults.XML_FILE_NAME)
            version_url = os.path.join(defaults.XML_DIR_NAME, defaults.VERSION_FILE_NAME)

        xml_file_path = cls.get_path_to_file_from_url(url)
        version_file_path = cls.get_path_to_file_from_url(version_url)

        if force_download or not os.path.exists(xml_file_path):

            log.info('download {} and {}'.format(xml_file_path, version_file_path))

            scheme = urlsplit(url).scheme

            if scheme in ('ftp', 'http'):
                urlretrieve(version_url, version_file_path)
                urlretrieve(url, xml_file_path)

            elif not scheme and os.path.isfile(url):
                shutil.copyfile(url, xml_file_path)
                shutil.copyfile(version_url, version_file_path)

        return xml_file_path, version_file_path

    @classmethod
    def get_path_to_file_from_url(cls, url):
        """standard file path
        
        :param str url: download URL
        """
        file_name = urlparse(url).path.split('/')[-1]
        return os.path.join(PYUNIPROT_DATA_DIR, file_name)

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


def update(connection=None, urls=None, force_download=False, taxids=None, silent=False):
    """Updates CTD database

    :param urls: list of urls to download
    :type urls: iterable
    :param connection: custom database connection string
    :type connection: str
    :param force_download: force method to download
    :type force_download: bool
    :param int,list,tuple taxids: int or iterable of NCBI taxonomy identifiers (default is None = load all)
    """
    if isinstance(taxids, int):
        taxids = (taxids,)
    db = DbManager(connection)
    db.db_import_xml(urls, force_download, taxids, silent)
    db.session.close()


def set_mysql_connection(host='localhost', user='pyuniprot_user', passwd='pyuniprot_passwd', db='pyuniprot',
                         charset='utf8'):
    """Method to set a MySQL connection

    :param host: MySQL database host
    :param user: MySQL database user
    :param passwd: MySQL database password
    :param db: MySQL database name
    :param charset: MySQL database charater set
    :return: None
    """
    connection_string = 'mysql+pymysql://{user}:{passwd}@{host}/{db}?charset={charset}'.format(
        host=host,
        user=user,
        passwd=passwd,
        db=db,
        charset=charset
    )
    set_connection(connection_string)

    return connection_string


def set_test_connection():
    set_connection(defaults.DEFAULT_SQLITE_TEST_DATABASE_NAME)


def set_connection(connection=defaults.sqlalchemy_connection_string_default):
    """
    Set the connection string for sqlalchemy and writes to the configuration file
    :param str connection: sqlalchemy connection string
    """
    cfp = defaults.config_file_path
    config = RawConfigParser()

    connection = connection.strip()

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
