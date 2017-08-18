# -*- coding: utf-8 -*-

import logging
import os
import shutil
import unittest
import datetime

import pyuniprot

from pandas.core.frame import DataFrame
from pyuniprot.constants import PYUNIPROT_DATA_DIR
from pyuniprot.manager.database import DbManager, BaseDbManager
from pyuniprot.manager.defaults import DEFAULT_TEST_DATABASE_LOCATION, sqlalchemy_connection_string_4_tests, \
    XML_FILE_NAME
from pyuniprot.manager import models

from pyuniprot.manager.query import QueryManager

log = logging.getLogger(__name__)

this_path = os.path.dirname(os.path.realpath(__file__))
test_xml_path = os.path.join(this_path, "data", XML_FILE_NAME)
connection_string = sqlalchemy_connection_string_4_tests


def download(cls, *args, **kwargs):
    """overwrites pyuniprot.manager.database.DbManager.download in TestImport.setup"""
    gziped_uniprot_file_loacation = os.path.join(PYUNIPROT_DATA_DIR, XML_FILE_NAME)
    shutil.copyfile(test_xml_path, gziped_uniprot_file_loacation)
    return gziped_uniprot_file_loacation


class TestQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DbManager.download = download
        pyuniprot.update(connection=connection_string)
        cls.query = QueryManager(connection=connection_string)
        cls.session = BaseDbManager(connection=connection_string).session

    @classmethod
    def tearDownClass(cls):
        os.remove(DEFAULT_TEST_DATABASE_LOCATION)
        shutil.rmtree(PYUNIPROT_DATA_DIR)
        cls.session.close()

    def test_number_of_inserts(self):
        models_list = [
            (models.Accession, 8),
            (models.AlternativeFullName, 3),
            (models.AlternativeShortName, 1),
            (models.DbReference, 184),
            (models.Disease, 1),
            (models.DiseaseComment, 1),
            (models.ECNumber, 1),
            (models.Entry, 4),
            (models.Feature, 74),
            (models.Function, 4),
            (models.Keyword, 29),
            (models.OrganismHost, 5),
            (models.OtherGeneName, 4),
            (models.Pmid, 18),
            (models.Sequence, 4),
            (models.SubcellularLocation, 8),
            (models.TissueInReference, 3),
            (models.TissueSpecificity, 1),
        ]
        for model, num_of_results in models_list:
            self.assertEqual(num_of_results, self.session.query(model).count())

    def test_query_accession(self):
        accessions = self.query.accession(entry_name='5HT2A_PIG', limit=1, as_df=False)

        accession = accessions[0]
        self.assertEqual(isinstance(accession, models.Accession), True)
        self.assertEqual(accession.accession, 'P50129')

        df = self.query.accession(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_alternative_full_name(self):
        alternative_full_names = self.query.alternative_full_name(
            name='Serotonin receptor 2A',
            entry_name='5HT2A_PIG',
            limit=1,
            as_df=False
        )

        alternative_full_name = alternative_full_names[0]
        self.assertEqual(isinstance(alternative_full_name, models.AlternativeFullName), True)
        self.assertEqual(alternative_full_name.name, 'Serotonin receptor 2A')

        df = self.query.alternative_full_name(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_alternative_short_name(self):
        alternative_short_names = self.query.alternative_short_name(entry_name='AAH_ARATH', limit=1, as_df=False)

        alternative_short_name = alternative_short_names[0]
        self.assertEqual(isinstance(alternative_short_name, models.AlternativeShortName), True)
        self.assertEqual(alternative_short_name.name, 'AtAAH')

        df = self.query.alternative_short_name(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_db_reference(self):
        db_references = self.query.db_reference(entry_name='5HT2A_PIG', limit=1, as_df=False)

        db_reference = db_references[0]
        self.assertEqual(isinstance(db_reference, models.DbReference), True)

        self.assertEqual((db_reference.identifier, db_reference.type_), ('S78208', 'EMBL'))

        df = self.query.db_reference(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_disease(self):
        diseases = self.query.disease(ref_id='177900', limit=1, as_df=False)

        disease = diseases[0]
        self.assertEqual(isinstance(disease, models.Disease), True)
        self.assertEqual(disease.name, 'Psoriasis 1')

        df = self.query.disease(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_disease_comment(self):
        disease_comments = self.query.disease_comment(entry_name='1C06_HUMAN', limit=1, as_df=False)

        disease_comment = disease_comments[0]
        self.assertEqual(isinstance(disease_comment, models.DiseaseComment), True)

        expected_comment = "Disease susceptibility is associated with variations affecting the " \
                           "gene represented in this entry."

        self.assertEqual(disease_comment.comment, expected_comment)

        df = self.query.disease_comment(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_ec_number(self):
        ec_numbers = self.query.ec_number(entry_name='AAH_ARATH', limit=1, as_df=False)

        ec_number = ec_numbers[0]
        self.assertEqual(isinstance(ec_number, models.ECNumber), True)
        self.assertEqual(ec_number.ec_number, '3.5.3.9')

        df = self.query.ec_number(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_entry(self):
        entries = self.query.entry(name='5HT2A_PIG', limit=1, as_df=False)

        entry = entries[0]
        self.assertEqual(isinstance(entry, models.Entry), True)

        expected_entry = {
            'created': datetime.date(1996, 10, 1),
            'dataset': 'Swiss-Prot',
            'gene_name': 'HTR2A',
            'modified': datetime.date(2017, 5, 10),
            'name': '5HT2A_PIG',
            'recommended_full_name': '5-hydroxytryptamine receptor 2A',
            'recommended_short_name': '5-HT-2',
            'taxid': 9823,
            'version': 111}

        for attribute, value in expected_entry.items():
            print(entry.__getattribute__(attribute))
            self.assertEqual(entry.__getattribute__(attribute), value)

        df = self.query.entry(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_feature(self):
        features = self.query.feature(entry_name='5HT2A_PIG', limit=1, as_df=False)

        feature = features[0]
        self.assertEqual(isinstance(feature, models.Feature), True)

        expected_feature = {
            'description': '5-hydroxytryptamine receptor 2A',
            'identifier': 'PRO_0000068949',
            'type_': 'chain'}

        for attribute, value in expected_feature.items():
            print(feature.__getattribute__(attribute))
            self.assertEqual(feature.__getattribute__(attribute), value)

        df = self.query.feature(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_function(self):
        functions = self.query.function(entry_name='001R_FRG3G', limit=1, as_df=False)
        function_ = functions[0]
        self.assertEqual(isinstance(function_, models.Function), True)
        self.assertEqual(function_.text, 'Transcription activation.')

        df = self.query.function(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_keyword(self):
        keywords = self.query.keyword(identifier='KW-0085', limit=1, as_df=False)

        keyword = keywords[0]
        self.assertEqual(isinstance(keyword, models.Keyword), True)
        self.assertEqual(keyword.name, 'Behavior')

        df = self.query.keyword(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_pmid(self):
        pmids = self.query.pmid( entry_name='5HT2A_PIG', limit=1, as_df=False)

        pmid = pmids[0]
        self.assertEqual(isinstance(pmid, models.Pmid), True)

        expected_pmid = {
            'date': 1995,
            'first': '201',
            'last': '206',
            'name': 'Biochim. Biophys. Acta',
            'pmid': 7794950,
            'title': 'Species differences in 5-HT2A receptors: cloned pig and rhesus monkey 5-HT2A receptors reveal '
                     'conserved transmembrane homology to the human rather than rat sequence.',
            'volume': 1236}

        for attribute, value in expected_pmid.items():
            print(pmid.__getattribute__(attribute))
            self.assertEqual(pmid.__getattribute__(attribute), value)

        df = self.query.pmid(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_sequence(self):
        sequences = self.query.sequence(entry_name='5HT2A_PIG', limit=1, as_df=False)

        sequence = sequences[0]
        self.assertEqual(isinstance(sequence, models.Sequence), True)
        self.assertEqual(sequence.sequence[-10:], 'NTVNEKVSCV')

        df = self.query.sequence(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_subcellular_location(self):
        subcellular_locations = self.query.subcellular_location(entry_name='AAH_ARATH', limit=1, as_df=False)

        subcellular_location = subcellular_locations[0]
        self.assertEqual(isinstance(subcellular_location, models.SubcellularLocation), True)
        self.assertEqual(subcellular_location.location, 'Endoplasmic reticulum')

        df = self.query.subcellular_location(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_tissue_in_reference(self):
        tissue_in_references = self.query.tissue_in_reference(entry_name='5HT2A_PIG', limit=1, as_df=False)

        tissue_in_reference = tissue_in_references[0]
        self.assertEqual(isinstance(tissue_in_reference, models.TissueInReference), True)
        self.assertEqual(tissue_in_reference.tissue, 'Pulmonary artery')

        df = self.query.tissue_in_reference(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_query_tissue_specificity(self):
        tissue_specificities = self.query.tissue_specificity(entry_name='AAH_ARATH', limit=1, as_df=False)

        tissue_specificity = tissue_specificities[0]
        self.assertEqual(isinstance(tissue_specificity, models.TissueSpecificity), True)
        self.assertEqual(tissue_specificity.comment, 'Expressed in seedlings, roots, stems, leaves, '
                                                       'flowers, siliques and seeds.')

        df = self.query.tissue_specificity(limit=1, as_df=True)
        self.assertEqual(isinstance(df, DataFrame), True)

    def test_prop_dbreference_types(self):
        self.assertEqual(len(self.query.dbreference_types), 60)

    def test_prop_taxids(self):
        self.assertEqual(set(self.query.taxids), set([9823, 3702, 9606, 654924]))

    def test_prop_datasets(self):
        self.assertEqual(self.query.datasets, ['Swiss-Prot'])

    def test_feature_types(self):
        self.assertEqual(len(self.query.feature_types), 15)

    def test_subcellular_locations(self):
        self.assertEqual(len(self.query.subcellular_locations), 8)

    def test_tissues_in_references(self):
        self.assertEqual(set(self.query.tissues_in_references), set(['Blood', 'Liver', 'Pulmonary artery']))

    def test_keywords(self):
        self.assertEqual(len(self.query.keywords), 29)

    def test_diseases(self):
        self.assertEqual(self.query.diseases, ['Psoriasis 1'])
