# -*- coding: utf-8 -*-

"""
This file contains a listing of the default CTD URLs.
"""
import os

from ..constants import PYUNIPROT_DIR, PYUNIPROT_DATA_DIR

DEFAULT_SQLITE_DATABASE_NAME = 'pyuniprot.db'
DEFAULT_SQLITE_TEST_DATABASE_NAME = 'pyuniprot_test.db'
DEFAULT_DATABASE_LOCATION = os.path.join(PYUNIPROT_DATA_DIR, DEFAULT_SQLITE_DATABASE_NAME)
DEFAULT_TEST_DATABASE_LOCATION = os.path.join(PYUNIPROT_DATA_DIR, DEFAULT_SQLITE_TEST_DATABASE_NAME)

XML_SPROT_URL = "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.xml.gz"
XML_FILE_NAME = os.path.basename(XML_SPROT_URL)

sqlalchemy_connection_string_default = 'sqlite:///' + DEFAULT_DATABASE_LOCATION
sqlalchemy_connection_string_4_tests = 'sqlite:///' + DEFAULT_TEST_DATABASE_LOCATION

sqlalchemy_connection_string_4_mysql = 'mysql+pymysql://pyuniprot:pyuniprot@localhost/pyuniprot?charset=utf8'
sqlalchemy_connection_string_4_mysql_tests = 'mysql+pymysql://pyuniprot:pyuniprotd@localhost/pyuniprot_test?charset=utf8'

XSD_URL = "http://www.uniprot.org/docs/uniprot.xsd"
XML_TAG_PREFIX = "{http://uniprot.org/uniprot}"

TABLE_PREFIX = 'pyuniprot_'

config_file_path = os.path.join(PYUNIPROT_DIR, 'config.ini')
