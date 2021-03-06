# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from backend.orcid import affiliate_author_with_orcid
from backend.orcid import OrcidPaperSource
from papers.models import Paper
from papers.models import Researcher
from backend.tests import PaperSourceTest

class OrcidUnitTest(unittest.TestCase):

    def test_affiliate_author(self):
        self.assertEqual(
                affiliate_author_with_orcid(
                    ('Jordi', 'Cortadella'),
                    '0000-0001-8114-250X',
                    [('N.', 'Nikitin'), ('J.', 'De San Pedro'), ('J.', 'Carmona'), ('J.', 'Cortadella')]),
                [None, None, None, '0000-0001-8114-250X'])
        self.assertEqual(
                affiliate_author_with_orcid(
                    ('Antonin', 'Delpeuch'),
                    '0000-0002-8612-8827',
                    [('Antonin', 'Delpeuch'), ('Anne', 'Preller')]),
                ['0000-0002-8612-8827', None])


class OrcidIntegrationTest(PaperSourceTest):

    @classmethod
    def setUpClass(self):
        super(OrcidIntegrationTest, self).setUpClass()
        self.source = OrcidPaperSource()

    def check_papers(self, papers):
        p = Paper.objects.get(
            title='From Natural Language to RDF Graphs with Pregroups')
        p.check_authors()
        author = p.authors[0]
        self.assertEqual(author.orcid, self.r4.orcid)
        p = Paper.objects.get(
            title='Complexity of Grammar Induction for Quantum Types')
        p.check_authors()
        author = p.authors[0]
        self.assertEqual(author.orcid, self.r4.orcid)

    def test_previously_present_papers_are_attributed(self):
        # Fetch papers from a researcher
        pablo = Researcher.get_or_create_by_orcid('0000-0002-6293-3231')
        self.source.fetch_and_save(pablo)

        p = Paper.objects.get(oairecord__doi='10.1007/978-3-642-25516-8_1')
        self.assertEqual(p.authors[2].orcid, pablo.orcid)

        # Now fetch a coauthor of him
        antoine = Researcher.get_or_create_by_orcid('0000-0002-7977-4441')
        self.source.fetch_and_save(antoine)

        # This paper should be attributed to both ORCID ids
        p = Paper.objects.get(oairecord__doi='10.1007/978-3-642-25516-8_1')

        self.assertEqual(p.authors[0].orcid, antoine.orcid)
        self.assertEqual(p.authors[2].orcid, pablo.orcid)

    def test_fetch_dois(self):
        pboesu = Researcher.get_or_create_by_orcid('0000-0001-6723-6833')
        self.source.fetch_and_save(pboesu)

        doi = '10.3354/meps09890'
        p = Paper.get_by_doi(doi)
        dois_in_paper = [r.doi for r in p.oairecords]
        self.assertTrue(doi in dois_in_paper)

    def test_orcid_affiliation(self):
        # this used to raise an error.
        # a more focused test might be preferable (focused on the said
        # paper)
        papers = list(self.source.fetch_orcid_records('0000-0002-9658-1473'))
        self.assertTrue(len(papers) > 30)

    def test_bibtex_fallback(self):
        papers = list(self.source.fetch_orcid_records('0000-0002-1900-3901'))
        titles = [paper.title for paper in papers]
        self.assertTrue('Company-Coq: Taking Proof General one step closer to a real IDE' in titles)

    def test_import_with_crossref_error(self):
        stergios = Researcher.get_or_create_by_orcid('0000-0001-9232-4042')
        self.source.fetch_and_save(stergios)
        p = Paper.objects.get(oairecord__doi='10.1016/j.metabol.2017.10.007')
        # crossref claims that the ORCID should be associated to author 2
        # but it should actually be associated to author 0
        self.assertEqual(p.authors[0].orcid, '0000-0001-9232-4042')
        self.assertEqual(p.authors[2].orcid, None)
        self.assertEqual(p.authors[0].researcher_id, stergios.id)
        self.assertEqual(p.authors[2].researcher_id, None)


