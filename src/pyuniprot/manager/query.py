# -*- coding: utf-8 -*-

from .database import BaseDbManager
from . import models
from sqlalchemy import distinct
from pandas import read_sql
from collections import Iterable


class QueryManager(BaseDbManager):
    """Query interface to database."""

    def _limit_and_df(self, query, limit, as_df=False):
        """adds a limit (limit==None := no limit) to any query and allow a return as pandas.DataFrame

        :param bool as_df: if is set to True results return as pandas.DataFrame
        :param `sqlalchemy.orm.query.Query` query: SQL Alchemy query 
        :param int limit: maximum number of results
        :return: query result of pyctd.manager.models.XY objects
        """
        if limit:
            query = query.limit(limit)

        if as_df:
            results = read_sql(query.statement, self.engine)
        else:
            results = query.all()

        return results

    @classmethod
    def _many_to_many_query(cls, query_obj, search4, model_attrib, many2many_attrib):
        model = model_attrib.parent.class_

        if isinstance(search4, str):
            query_obj = query_obj.session.query(model).filter(model_attrib.any(many2many_attrib.like(search4)))
        elif isinstance(search4, int):
            query_obj = query_obj.session.query(model).filter(model_attrib.any(many2many_attrib == search4))
        elif isinstance(search4, Iterable):
            query_obj = query_obj.session.query(model).filter(model_attrib.any(many2many_attrib.in_(search4)))

        return query_obj

    @classmethod
    def _one_to_many_query(cls, query_obj, search4, model_attrib):
        model = model_attrib.parent.class_

        if isinstance(search4, str):
            query_obj = query_obj.join(model).filter(model_attrib.like(search4))
        elif isinstance(search4, int):
            query_obj = query_obj.join(model).filter(model_attrib == search4)
        elif isinstance(search4, Iterable):
            query_obj = query_obj.join(model).filter(model_attrib.in_(search4))
        return query_obj

    @classmethod
    def _model_query(cls, query_obj, search4, model_attrib):

        if isinstance(search4, str):
            query_obj = query_obj.filter(model_attrib.like(search4))
        elif isinstance(search4, int):
            query_obj = query_obj.filter(model_attrib == search4)
        elif isinstance(search4, Iterable):
            query_obj = query_obj.filter(model_attrib.in_(search4))
        return query_obj

    def get_obo_string(self, taxid=None, limit=None):

        q = self.session.query(models.Entry)

        if limit:
            q = q.limit(limit)
        if taxid:
            q = q.filter(models.Entry.taxid == taxid)

        obo_string = ''

        for entry in q.all():
            obo_string += '\n[Term]\nid: SWISSPROT:{}\n'.format(entry.accessions[0])
            if len(entry.accessions) > 1:
                for accession in entry.accessions[1:]:
                    obo_string += 'alt_id: {}\n'.format(accession)
            obo_string += 'name: {}\n'.format(entry.recommended_full_name)
            for alternative_name in entry.alternative_names:
                obo_string += 'synonym: "{}" EXACT ALTERNATIVE_NAME []\n'.format(alternative_name.fullName)
            obo_string += 'synonym: "{}" EXACT GENE_NAME []\n'.format(entry.gene_name)
            for xref in entry.db_references:
                if xref.type in ['GO', 'HGNC']:
                    xref.identifier = ':'.join(xref.identifier.split(':')[1:])
                    obo_string += 'xref: {}:{}\n'.format(xref.type, xref.identifier.replace('\\', '\\\\'))
        return obo_string

    def get_model_queries(self, query_obj, model_queries_config):
        for search4, model_attrib in model_queries_config:
            query_obj = self._model_query(query_obj, search4, model_attrib)
        return query_obj

    def get_one_to_many_queries(self, query_obj, one_to_many_queries):
        for search4, model_attrib in one_to_many_queries:
            query_obj = self._one_to_many_query(query_obj, search4, model_attrib)
        return query_obj

    def get_many_to_many_queries(self, query_obj, many_to_many_queries_config):
        for search4, model_attrib, many2many_attrib in many_to_many_queries_config:
            query_obj = self._many_to_many_query(query_obj, search4, model_attrib, many2many_attrib)
        return query_obj

    def get_entry(self,
                  id=None,
                  name=None,
                  recommended_full_name=None,
                  recommended_short_name=None,
                  gene_name=None,
                  taxid=None,
                  accessions=None,
                  organism_hosts = None,
                  feature_types=None,
                  functions=None,
                  ec_numbers=None,
                  db_reference_identifiers=None,
                  alternative_names=None,
                  disease_comments=None,
                  disease_names=None,
                  tissue_specificities=None,
                  pmids=None,
                  keywords=None,
                  subcellular_locations=None,
                  tissue_in_reference=None,
                  limit=None,
                  as_df=False):
        """
        Get entry

        :param tissue_in_reference:
        :param subcellular_locations:
        :param keywords:
        :param pmids:
        :param tissue_specificities:
        :param disease_comments:
        :param alternative_names:
        :param db_reference_identifiers:
        :param ec_numbers:
        :param functions:
        :param feature_types:
        :param organism_hosts:
        :param accessions:
        :param disease_names:
        :param str name: UniProt protein name
        :param str recommended_full_name: recommended full protein name
        :param str recommended_short_name: recommended short protein name
        :param str gene_name: gene name
        :param int taxid: NCBI taxonomy identifier
        :param int limit: maximum number of results
        :param bool as_df: if set to True result returns as `pandas.DataFrame`

        :return: list of :class:`pyctd.manager.models.Disease` object


        .. seealso::

            :class:`pyuniprot.manager.models.Entry`
        """
        q = self.session.query(models.Entry)

        model_queries_config = (
            (id, models.Entry.id),
            (name, models.Entry.name),
            (recommended_full_name, models.Entry.recommended_full_name),
            (gene_name, models.Entry.gene_name),
            (taxid, models.Entry.taxid)
        )
        q = self.get_model_queries(q, model_queries_config)

        one_to_many_queries_config = (
            (accessions, models.Accession.accession),
            (organism_hosts, models.OrganismHost.taxid),
            (feature_types, models.Feature.type),
            (functions, models.Function.text),
            (ec_numbers, models.ECNumber.ec_number),
            (db_reference_identifiers, models.DbReference.identifier),
            (alternative_names, models.AlternativeFullName.name),
            (disease_comments, models.DiseaseComment.comment),
            (tissue_specificities, models.TissueSpecificity.comment),
        )
        self.get_one_to_many_queries(q, one_to_many_queries_config)

        many_to_many_queries_config = (
            (pmids, models.Entry.pmids, models.Pmid.pmid),
            (keywords, models.Entry.keywords, models.Keyword.identifier),
            (subcellular_locations, models.Entry.subcellular_locations, models.SubcellularLocation.location),
            (tissue_in_reference, models.Entry.tissue_in_references, models.TissueInReference.tissue)
        )
        self.get_many_to_many_queries(q, many_to_many_queries_config)

        if disease_names:
            q = q.join(models.Entry.disease_comments).join(models.DiseaseComment.disease)
            if isinstance(disease_names, str):
                q = q.filter(models.Disease.name.like(disease_names))
            elif isinstance(disease_names, Iterable):
                q = q.filter(models.Disease.name.in_(disease_names))

        return self._limit_and_df(q, limit, as_df)

    def get_disease(self,
                    identifier=None,
                    ref_id=None,
                    ref_type=None,
                    name=None,
                    acronym=None,
                    description=None,
                    limit=None,
                    as_df=False
                    ):
        """
        :param id:
        :param identifier:
        :param ref_id:
        :param ref_type:
        :param name:
        :param acronym:
        :param description:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.Disease)

        model_queries_config = (
            (identifier, models.Disease.identifier),
            (ref_id, models.Disease.ref_id),
            (ref_type, models.Disease.ref_type),
            (name, models.Disease.name),
            (acronym, models.Disease.acronym),
            (description, models.Disease.description)
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_disease_comment(self, comment=None, limit=None, as_df=False):
        """

        :param comment:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.DiseaseComment)

        model_queries_config = (
            (comment, models.DiseaseComment.comment),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_alternative_full_name(self, name=None, limit=None, as_df=False):
        """

        :param name:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.AlternativeFullName)

        model_queries_config = (
            (name, models.AlternativeFullName.name),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_alternative_short_name(self, name=None, limit=None, as_df=False):
        """

        :param name:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.AlternativeShortName)

        model_queries_config = (
            (name, models.AlternativeShortName.name),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_accession(self, accession=None, limit=None, as_df=False):
        """

        :param accession:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.Accession)

        model_queries_config = (
            (accession, models.Accession.accession),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_pmid(self,
                 pmid=None,
                 last=None,
                 first=None,
                 volume=None,
                 name=None,
                 date=None,
                 type_=None,
                 title=None,
                 limit=None,
                 as_df=False
                 ):
        """

        :param pmid:
        :param last:
        :param first:
        :param volume:
        :param name:
        :param date:
        :param type_:
        :param title:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.Pmid)

        model_queries_config = (
            (pmid, models.Pmid.pmid),
            (last, models.Pmid.last),
            (first, models.Pmid.first),
            (volume, models.Pmid.volume),
            (name, models.Pmid.name),
            (date, models.Pmid.date),
            (type_, models.Pmid.type_),
            (title, models.Pmid.title)
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_organismHost(self, taxid=None, limit=None, as_df=None):
        """

        :param taxid:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.OrganismHost)

        if taxid:
            q = q.filter(models.OrganismHost.taxid(taxid))

        return self._limit_and_df(q, limit, as_df)

    def get_dbReference(self, type_=None, identifier=None, limit=None, as_df=None):
        """

        :param type_:
        :param identifier:
        :return:
        """
        q = self.session.query(models.DbReference)

        model_queries_config = (
            (type_, models.DbReference.type),
            (identifier, models.DbReference.identifier)
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_feature(self, type_=None, identifier=None, description=None, limit=None, as_df=None):
        """

        :param type_:
        :param identifier:
        :param description:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.Feature)

        model_queries_config = (
            (type_, models.Feature.type),
            (identifier, models.Feature.identifier),
            (description, models.Feature.description)
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_function(self, text=None, limit=None, as_df=None):
        """

        :param text:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.Function)

        model_queries_config = (
            (text, models.Function.text),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_keyword(self, name=None, identifier=None, limit=None, as_df=None):
        """

        :param name:
        :param identifier:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.Keyword)

        model_queries_config = (
            (name, models.Keyword.name),
            (identifier, models.Keyword.identifier)
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_ec_number(self, ec_number=None, limit=None, as_df=None):
        """

        :param ec_number:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.ECNumber)

        model_queries_config = (
            (ec_number, models.ECNumber.ec_number),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_subcellular_location(self, location=None, limit=None, as_df=None):
        """

        :param location:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.SubcellularLocation)

        model_queries_config = (
            (location, models.SubcellularLocation.location),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_tissue_specificity(self, comment, limit=None, as_df=None):
        """

        :param comment:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.TissueSpecificity)

        model_queries_config = (
            (comment, models.TissueSpecificity.comment),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)

    def get_tissue_in_reference(self, tissue=None, limit=None, as_df=None):
        """

        :param tissue:
        :param limit:
        :param as_df:
        :return:
        """
        q = self.session.query(models.TissueInReference)

        model_queries_config = (
            (tissue, models.TissueInReference.tissue),
        )
        q = self.get_model_queries(q, model_queries_config)

        return self._limit_and_df(q, limit, as_df)


    @property
    def dbreference_types(self):
        """
        :return: List of strings for all available database cross reference types used in model DbReference
        :rtype: list of :class:`str`
        """
        q = self.session.query(distinct(models.DbReference.type))
        return [x[0] for x in q.all()]

    @property
    def taxids(self):
        """
        :return: List of strings for all NCBI taxonomy identifiers
        :rtype: list
        """
        r = self.session.query(distinct(models.Entry.taxid)).all()
        return [x[0] for x in r]

    @property
    def datasets(self):
        """
        :return: List of strings for all dataset types (SwissProt, TrEMBL)
        :rtype: list
        """
        r = self.session.query(distinct(models.Entry.dataset)).all()
        return [x[0] for x in r]

    @property
    def feature_types(self):
        """
        :return: List of strings for feature types used in model Feature
        :rtype: list
        """
        r = self.session.query(distinct(models.Feature.type)).all()
        return [x[0] for x in r]

    @property
    def subcellular_locations(self):
        """
        :return: List of all distinct SubcellularLocation model objects
        """
        return self.session.query(models.SubcellularLocation).all()

    @property
    def tissues_in_references(self):
        """
        :return: List of all distinct TissueInReference model objects
        """
        return self.session.query(models.TissueInReference).all()

    @property
    def keywords(self):
        """
        :return: List of all distinct TissueInReference model objects
        """
        return self.session.query(models.Keyword).all()
