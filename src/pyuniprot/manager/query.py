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
        :param int or tuple[int] limit: maximum number of results
        :return: query result of pyuniprot.manager.models.XY objects
        """
        if limit:

            if isinstance(limit, int):
                query = query.limit(limit)

            if isinstance(limit, Iterable) and len(limit) == 2 and [int, int] == [type(x) for x in limit]:
                page, page_size = limit
                query = query.limit(page_size)
                query = query.offset(page * page_size)

        if as_df:
            results = read_sql(query.statement, self.engine)

        else:
            results = query.all()

        return results

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

            for alternative_name in entry.alternative_full_names     + entry.alternative_short_names:
                obo_string += 'synonym: "{}" EXACT ALTERNATIVE_NAME []\n'.format(alternative_name.name)

            obo_string += 'synonym: "{}" EXACT GENE_NAME []\n'.format(entry.gene_name)

            for xref in entry.db_references:
                if xref.type_ in ['GO', 'HGNC']:
                    xref.identifier = ':'.join(xref.identifier.split(':')[1:])
                    obo_string += 'xref: {}:{}\n'.format(xref.type_, xref.identifier.replace('\\', '\\\\'))
        return obo_string

    def get_model_queries(self, query_obj, model_queries_config):
        for search4, model_attrib in model_queries_config:

            if search4 is not None:
                query_obj = self._model_query(query_obj, search4, model_attrib)
        return query_obj

    def get_one_to_many_queries(self, query_obj, one_to_many_queries):
        for search4, model_attrib in one_to_many_queries:
            if search4 is not None:
                query_obj = self._one_to_many_query(query_obj, search4, model_attrib)
        return query_obj

    def get_many_to_many_queries(self, query_obj, many_to_many_queries_config):
        for search4, model_attrib, many2many_attrib in many_to_many_queries_config:
            if search4 is not None:
                query_obj = self._many_to_many_query(query_obj, search4, model_attrib, many2many_attrib)
        return query_obj

    @classmethod
    def _many_to_many_query(cls, query_obj, search4, join_attrib, many2many_attrib):

        if isinstance(search4, str):
            query_obj = query_obj.join(join_attrib).filter(many2many_attrib.like(search4))

        elif isinstance(search4, int):
            query_obj = query_obj.join(join_attrib).filter(many2many_attrib == search4)

        elif isinstance(search4, Iterable):
            query_obj = query_obj.join(join_attrib).filter(many2many_attrib.in_(search4))

        return query_obj

    @classmethod
    def _one_to_many_query(cls, query_obj, search4, model_attrib):
        """extends and returns a SQLAlchemy query object to allow one-to-many queries

        :param query_obj: SQL Alchemy query object
        :param str search4: search string
        :param model_attrib: attribute in model
        """
        model = model_attrib.parent.class_

        if isinstance(search4, str):
            query_obj = query_obj.join(model).filter(model_attrib.like(search4))

        elif isinstance(search4, int):
            query_obj = query_obj.join(model).filter(model_attrib == search4)

        elif isinstance(search4, Iterable):
            query_obj = query_obj.join(model).filter(model_attrib.in_(search4))

        return query_obj

    def keyword(self, name=None, identifier=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.Keyword` objects in database

        :param name: keyword name(s)
        :type name: str or tuple(str) or None

        :param identifier: keyword identifier(s)
        :type identifier: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type identifier: str or tuple(str) or None


        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Keyword`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Keyword`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.Keyword)

        model_queries_config = (
            (name, models.Keyword.name),
            (identifier, models.Keyword.identifier)
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_many_to_many_queries(q, ((entry_name, models.Keyword.entries, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def entry(self,
              name=None,
              dataset=None,
              recommended_full_name=None,
              recommended_short_name=None,
              gene_name=None,
              taxid=None,
              accession=None,
              organism_host=None,
              feature_type=None,
              function_=None,
              ec_number=None,
              db_reference=None,
              alternative_name=None,
              disease_comment=None,
              disease_name=None,
              tissue_specificity=None,
              pmid=None,
              keyword=None,
              subcellular_location=None,
              tissue_in_reference=None,
              sequence=None,
              limit=None,
              as_df=False):
        """Method to query :class:`.models.Entry` objects in database

        An entry is the root element in UniProt datasets. Everything is linked to entry and can be accessed from

        :param name: UniProt entry name(s)
        :type name: str or tuple(str) or None

        :param dataset: Swiss-Prot or TrEMBL
        :type name: str or tuple(str) or None

        :param recommended_full_name: recommended full protein name(s)
        :type recommended_full_name: str or tuple(str) or None

        :param recommended_short_name: recommended short protein name(s)
        :type recommended_short_name: str or tuple(str) or None

        :param tissue_in_reference: tissue(s) mentioned in reference
        :type tissue_in_reference: str or tuple(str) or None

        :param subcellular_location: subcellular location(s)
        :type subcellular_location: str or tuple(str) or None

        :param keyword: keyword(s)
        :type keyword: str or tuple(str) or None

        :param pmid: PubMed identifier(s)
        :type pmid: int or tuple(int) or None

        :param tissue_specificity: tissue specificit(y/ies)
        :type tissue_specificity: str or tuple(str) or None

        :param disease_comment: disease_comment(s)
        :type disease_comment: str or tuple(str) or None

        :param alternative_name: alternative name(s)
        :type alternative_name: str or tuple(str) or None

        :param db_reference: cross reference identifier(s)
        :type db_reference: str or tuple(str) or None

        :param ec_number: enzyme classification number(s), e.g. 1.1.1.1
        :type ec_number: str or tuple(str) or None

        :param function_: description of protein function(s)
        :type function_: str or tuple(str) or None

        :param feature_type: feature type(s)
        :type feature_type: str or tuple(str) or None

        :param organism_host: organism host(s) as taxid(s)
        :type organism_host: int or tuple(int) or None

        :param accession: UniProt accession number(s)
        :type accession: str or tuple(str) or None

        :param disease_name: disease name(s)
        :type disease_name: str or tuple(str) or None

        :param gene_name: gene name(s)
        :type gene_name: str or tuple(str) or None

        :param taxid: NCBI taxonomy identifier(s)
        :type taxid: int or tuple(int) or None

        :param sequence: Amino acid sequence(s)
        :type sequence: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Entry`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Entry`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.Entry)

        model_queries_config = (
            (dataset, models.Entry.dataset),
            (name, models.Entry.name),
            (recommended_full_name, models.Entry.recommended_full_name),
            (recommended_short_name, models.Entry.recommended_short_name),
            (gene_name, models.Entry.gene_name),
            (taxid, models.Entry.taxid),
        )
        q = self.get_model_queries(q, model_queries_config)

        one_to_many_queries_config = (
            (accession, models.Accession.accession),
            (organism_host, models.OrganismHost.taxid),
            (feature_type, models.Feature.type_),
            (function_, models.Function.text),
            (ec_number, models.ECNumber.ec_number),
            (db_reference, models.DbReference.identifier),
            (alternative_name, models.AlternativeFullName.name),
            (disease_comment, models.DiseaseComment.comment),
            (tissue_specificity, models.TissueSpecificity.comment),
            (sequence, models.Sequence.sequence),
        )
        q = self.get_one_to_many_queries(q, one_to_many_queries_config)

        many_to_many_queries_config = (
            (pmid, models.Entry.pmids, models.Pmid.pmid),
            (keyword, models.Entry.keywords, models.Keyword.name),
            (subcellular_location, models.Entry.subcellular_locations, models.SubcellularLocation.location),
            (tissue_in_reference, models.Entry.tissue_in_references, models.TissueInReference.tissue)
        )
        q = self.get_many_to_many_queries(q, many_to_many_queries_config)

        if disease_name:
            q = q.join(models.Entry.disease_comments).join(models.DiseaseComment.disease)
            if isinstance(disease_name, str):
                q = q.filter(models.Disease.name.like(disease_name))
            elif isinstance(disease_name, Iterable):
                q = q.filter(models.Disease.name.in_(disease_name))

        return self._limit_and_df(q, limit, as_df)

    def disease(self,
                identifier=None,
                ref_id=None,
                ref_type=None,
                name=None,
                acronym=None,
                description=None,
                entry_name=None,
                limit=None,
                as_df=False
                ):
        """Method to query :class:`.models.Disease` objects in database


        :param identifier: disease UniProt identifier(s)
        :type identifier: str or tuple(str) or None

        :param ref_id: identifier(s) of referenced database
        :type ref_id: str or tuple(str) or None

        :param ref_type: database name(s)
        :type ref_type: str or tuple(str) or None

        :param name: disease name(s)
        :type name: str or tuple(str) or None

        :param acronym: disease acronym(s)
        :type acronym: str or tuple(str) or None

        :param description: disease description(s)
        :type description: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Disease`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Disease`) or :class:`pandas.DataFrame`
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

        if entry_name:
            q = q.session.query(models.Disease).join(models.DiseaseComment).join(models.Entry)
            if isinstance(entry_name, str):
                q = q.filter(models.Entry.name == entry_name)
            elif isinstance(entry_name, Iterable):
                q = q.filter(models.Entry.name.in_(entry_name))

        return self._limit_and_df(q, limit, as_df)

    def disease_comment(self, comment=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.DiseaseComment` objects in database

        :param comment: Comment(s) to disease
        :type comment: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.DiseaseComment`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.DiseaseComment`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.DiseaseComment)

        q = self.get_model_queries(q, ((comment, models.DiseaseComment.comment),))

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def other_gene_name(self, type_=None, name=None, entry_name=None, limit=None, as_df=None):
        """Method to query :class:`.models.OtherGeneName` objects in database

        :param type_: type(s) of gene name e.g. *synonym*
        :type type_: str or tuple(str) or None

        :param name: other gene name(s)
        :type name: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.OtherGeneName`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.OtherGeneName`) or :class:`pandas.DataFrame`

        """
        q = self.session.query(models.OtherGeneName)

        model_queries_config = (
            (type_, models.OtherGeneName.type_),
            (name, models.OtherGeneName.name),
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def alternative_full_name(self, name=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.AlternativeFullName` objects in database

        :param name: alternative full name(s)
        :type name: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.AlternativeFullName`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.AlternativeFullName`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.AlternativeFullName)

        model_queries_config = (
            (name, models.AlternativeFullName.name),
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def alternative_short_name(self, name=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.AlternativeShortlName` objects in database

        :param name: alternative short name(s)
        :type name: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.AlternativeShortName`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.AlternativeShortName`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.AlternativeShortName)

        model_queries_config = (
            (name, models.AlternativeShortName.name),
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def accession(self, accession=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.Accession` objects in database

        :param accession: UniProt Accession number(s)
        :type accession: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Accession`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Accession`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.Accession)

        model_queries_config = (
            (accession, models.Accession.accession),
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def pmid(self,
             pmid=None,
             entry_name=None,
             first=None,
             last=None,
             volume=None,
             name=None,
             date=None,
             title=None,
             limit=None,
             as_df=False
             ):
        """Method to query :class:`.models.Pmid` objects in database

        :param pmid: PubMed identifier(s)
        :type pmid: int or tuple(int) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param first: first page(s)
        :type first: str or tuple(str) or None

        :param last: last page(s)
        :type last: str or tuple(str) or None

        :param volume: volume(s)
        :type volume: int or tuple(int) or None

        :param name: name(s) of journal
        :type name: str or tuple(str) or None

        :param date: publication year(s)
        :type date: int or tuple(int) or None

        :param title: title(s) of publication
        :type title: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Pmid`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Pmid`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.Pmid)

        model_queries_config = (
            (pmid, models.Pmid.pmid),
            (last, models.Pmid.last),
            (first, models.Pmid.first),
            (volume, models.Pmid.volume),
            (name, models.Pmid.name),
            (date, models.Pmid.date),
            (title, models.Pmid.title)
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_many_to_many_queries(q, ((entry_name, models.Pmid.entries, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def organism_host(self, taxid=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.OrganismHost` objects in database

        :param taxid: NCBI taxonomy identifier(s)
        :type taxid: int or tuple(int) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.OrganismHost`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.OrganismHost`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.OrganismHost)

        q = self.get_model_queries(q, ((taxid, models.OrganismHost.taxid),))

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def db_reference(self, type_=None, identifier=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.DbReference` objects in database

        Check list of available databases with on :py:attr:`.dbreference_types`

        :param type_: type(s) (or name(s)) of database
        :type type_: str or tuple(str) or None

        :param identifier: unique identifier(s) in specific database (type)
        :type identifier: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.DbReference`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.DbReference`) or :class:`pandas.DataFrame`

        **Links**

            - `UniProt dbxref <http://www.uniprot.org/docs/dbxref>`_
        """
        q = self.session.query(models.DbReference)

        model_queries_config = (
            (type_, models.DbReference.type_),
            (identifier, models.DbReference.identifier)
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def feature(self, type_=None, identifier=None, description=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.Feature` objects in database

        Check available features types with ``pyuniprot.query().feature_types``

        :param type_: type(s) of feature
        :type type_: str or tuple(str) or None

        :param identifier: feature identifier(s)
        :type identifier: str or tuple(str) or None

        :param description: description(s) of feature(s)
        :type description: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Feature`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Feature`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.Feature)

        model_queries_config = (
            (type_, models.Feature.type_),
            (identifier, models.Feature.identifier),
            (description, models.Feature.description)
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def function(self, text=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.Function` objects in database

        :param text: description(s) of function(s)
        :type text: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Function`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Function`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.Function)

        model_queries_config = (
            (text, models.Function.text),
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def ec_number(self, ec_number=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.ECNumber` objects in database

        :param ec_number: Enzyme Commission number(s)
        :type ec_number: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.ECNumber`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.ECNumber`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.ECNumber)

        q = self.get_model_queries(q, ((ec_number, models.ECNumber.ec_number),))

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def sequence(self, sequence=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.Sequence` objects in database

        :param sequence: AA sequence(s)
        :type sequence: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.Sequence`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.Sequence`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.Sequence)

        q = self.get_model_queries(q, ((sequence, models.Sequence.sequence),))

        q = self.get_many_to_many_queries(q, ((entry_name, models.SubcellularLocation.entries, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def subcellular_location(self, location=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.SubcellularLocation` objects in database

        :param location: subcellular location(s)
        :type location: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.SubcellularLocation`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.SubcellularLocation`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.SubcellularLocation)

        q = self.get_model_queries(q, ((location, models.SubcellularLocation.location),))

        q = self.get_many_to_many_queries(q, ((entry_name, models.SubcellularLocation.entries, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def tissue_specificity(self, comment=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.TissueSpecificity` objects in database

        Provides information on the expression of a gene at the mRNA or protein level in cells or in tissues of
        multicellular organisms. By default, the information is derived from experiments at the mRNA level, unless
        specified ‘at protein level

        :param comment: Comment(s) describing tissue specificity
        :type comment: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.TissueSpecificity`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.TissueSpecificity`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.TissueSpecificity)

        q = self.get_model_queries(q, ((comment, models.TissueSpecificity.comment),))

        q = self.get_one_to_many_queries(q, ((entry_name, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    def tissue_in_reference(self, tissue=None, entry_name=None, limit=None, as_df=False):
        """Method to query :class:`.models.TissueInReference` objects in database

        :param tissue: tissue(s) linked to reference
        :type tissue: str or tuple(str) or None

        :param entry_name: name(s) in :class:`.models.Entry`
        :type entry_name: str or tuple(str) or None

        :param limit:
            - if `isinstance(limit,int)==True` -> limit
            - if `isinstance(limit,tuple)==True` -> format:= tuple(page_number, results_per_page)
            - if limit == None -> all results
        :type limit: int or tuple(int) or None

        :param bool as_df: if `True` results are returned as :class:`pandas.DataFrame`

        :return:
            - if `as_df == False` -> list(:class:`.models.TissueInReference`)
            - if `as_df == True`  -> :class:`pandas.DataFrame`
        :rtype: list(:class:`.models.TissueInReference`) or :class:`pandas.DataFrame`
        """
        q = self.session.query(models.TissueInReference)

        model_queries_config = (
            (tissue, models.TissueInReference.tissue),
        )
        q = self.get_model_queries(q, model_queries_config)

        q = self.get_many_to_many_queries(q, ((entry_name, models.TissueInReference.entries, models.Entry.name),))

        return self._limit_and_df(q, limit, as_df)

    @property
    def dbreference_types(self):
        """Distinct database reference types (``type_``) in :class:`.models.DbReference`

        :return: List of strings for all available database cross reference types used in model DbReference
        :rtype: list[str]
        """
        q = self.session.query(distinct(models.DbReference.type_))
        return [x[0] for x in q.all()]

    @property
    def taxids(self):
        """Distinct NCBI taxonomy identifiers (``taxid``) in :class:`.models.Entry`

        :return: NCBI taxonomy identifiers
        :rtype: list[int]
        """
        r = self.session.query(distinct(models.Entry.taxid)).all()
        return [x[0] for x in r]

    @property
    def datasets(self):
        """Distinct datasets (``dataset``) in :class:`.models.Entry`

        Distinct datasets are SwissProt or/and TrEMBL

        :return: all distinct dataset types
        :rtype: list[str]
        """
        r = self.session.query(distinct(models.Entry.dataset)).all()
        return [x[0] for x in r]

    @property
    def feature_types(self):
        """Distinct types (``type_``) in :class:`.models.Feature`

        :return: all distinct feature types
        :rtype: list[str]
        """
        r = self.session.query(distinct(models.Feature.type_)).all()
        return [x[0] for x in r]

    @property
    def subcellular_locations(self):
        """Distinct subcellular locations (``location`` in :class:`.models.SubcellularLocation`)

        :return: all distinct subcellular locations
        :rtype: list[str]
        """
        return [x[0] for x in self.session.query(models.SubcellularLocation.location).all()]

    @property
    def tissues_in_references(self):
        """Distinct tissues (``tissue`` in :class:`.models.TissueInReference`)

        :return: all distinct tissues in references
        :rtype: list[str]
        """
        return [x[0] for x in self.session.query(models.TissueInReference.tissue).all()]

    @property
    def keywords(self):
        """Distinct keywords (``name`` in :class:`.models.Keyword`)

        :returns: all distinct keywords
        :rtype: list[str]
        """
        return [x[0] for x in self.session.query(models.Keyword.name).all()]

    @property
    def diseases(self):
        """Distinct diseases (``name`` in :class:`.models.Disease`)

        :returns: all distinct disease names
        :rtype: list[str]
        """
        return [x[0] for x in self.session.query(models.Disease.name).all()]

    @property
    def version(self):
        """Version of UniPort knowledgebase

        :returns: dictionary with version info
        :rtype: dict
        """
        return [x for x in self.session.query(models.Version).all()]

