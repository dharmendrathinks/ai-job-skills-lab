"""P5 owned-fixture behavioral checks; not real coverage or language quality claims."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.research_evidence import Store, EvidenceError
from tools.research_coverage import (coverage, register_protocol, assess_capture, define_cohort, compare,
                                     review_segments, register_board, link_board, vacancy_view)
from tools.research_languages import translate, review_translation, freeze_gold, evaluate_languages
from tools.research_context import import_context
from tools.research_global import registry
from tests.test_research_evidence import bundle, annotation, BODY
from tests.test_research_decisions import context_bundle

START = datetime(2026,9,8,tzinfo=timezone.utc)


class GlobalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.now = START + timedelta(days=6)
        self.store = Store(Path(self.temp.name)/'state', clock=lambda:self.now)

    def payload(self,key):
        with self.store.transaction() as s: return deepcopy(s['artifacts'][key]['payload'])

    def protocol(self, source='synthetic-owned', **kw):
        row = {'schema_version':1, 'source':source, 'instance':'owned', 'board':'owned', 'query':'retrieval',
               'requested_filters':{}, 'effective_filters':{}, 'collector_version':'owned/1', 'query_pack_version':'owned-en/1',
               'scope':'bounded-sample', 'cadence_seconds':86400, 'capture_offset_seconds':3600,'capture_tolerance_seconds':60, 'reviewer':'fixture author', 'limitations':['Owned fixture only.'], **kw}
        return register_protocol(self.store,row)['protocol']

    def capture(self, day, *, source='synthetic-owned', ids=('req-1',), protocol=None, complete='complete-request',
                fresh=True, terminal=None, changes=(), query='retrieval', description=BODY):
        date = START + timedelta(days=day,hours=1)
        data = bundle(source); template = data['observations'][0]
        data['policy']['reviewed_at'] = START.isoformat()
        data['receipt'].update(query=query, requested_filters={}, effective_filters={}, started_at=date.isoformat(),
                               finished_at=date.isoformat(), completeness=complete,
                               pages=[{'locator':'https://owned.example/board', 'status':'failed' if complete=='failed' else 'ok', 'returned':len(ids), 'next_cursor':None}])
        data['observations'] = [{**template,'native_id':i,'employer_requisition':i,'captured_at':date.isoformat(),
                                 'source_revision':f'{i}:{day}', 'description':description} for i in ids]
        result = self.store.import_bundle(data)
        if protocol:
            result['capture'] = assess_capture(self.store, {'schema_version':1,'receipt':result['receipt'],'protocol':protocol,
                'fresh':fresh,'terminal':complete=='complete-request' if terminal is None else terminal,
                'evidence':'Owned fixture complete inventory/request; not actual provider validation.', 'reviewer':'fixture','changes':list(changes)})['capture']
        return result

    def cohort(self, protocols, basis='capture'):
        return define_cohort(self.store, {'schema_version':1,'name':'Owned equal windows','protocols':protocols,'basis':basis,
                'windows':[{'from':START.isoformat(),'to':(START+timedelta(days=2)).isoformat()},
                           {'from':(START+timedelta(days=2)).isoformat(),'to':(START+timedelta(days=4)).isoformat()}],
                'reviewer':'fixture','limitations':['Two-day fixture, not target 28-day human research.']})['cohort']

    def populated(self):
        p=self.protocol(); captures=[self.capture(d,protocol=p,ids=('req-1',) if d<2 else ('req-1','req-2')) for d in range(4)]
        return p,captures

    def test_all_candidates_have_explicit_disposition(self):
        data=registry(); self.assertEqual(len(data['sources']),16)
        self.assertEqual([s['id'] for s in data['sources'] if s['disposition']=='go-limited'],['jobicy'])

    def test_coverage_deduplicates_revisions_and_discloses_missing_segments(self):
        self.capture(0); self.capture(1)
        report=coverage(self.store,expected={'countries':['IN','DE'],'language':['de']})
        self.assertEqual(report['counts']['deduplicated_openings'],1)
        self.assertEqual(report['missing_segments']['language'],['de'])
        data=self.payload(report['coverage']); self.assertEqual(data['untranslated_observations'],1)
        self.assertEqual(data['source_health']['synthetic-owned']['receipts'],2)

    def test_equal_stable_windows_report_sample_delta_only(self):
        p,_=self.populated(); result=compare(self.store,self.cohort([p]))
        self.assertEqual(result['status'],'comparable-sample'); self.assertEqual(result['opening_delta'],1)
        data=self.payload(result['comparison']); self.assertIsNone(data['capability_deltas'])
        self.assertEqual(data['capability_comparison'],'insufficient-or-changed-analysis')

    def test_source_addition_does_not_appear_as_growth(self):
        p,_=self.populated(); self.capture(2,source='new-owned',ids=('extra',)); self.capture(3,source='new-owned',ids=('extra-2',))
        result=compare(self.store,self.cohort([p])); self.assertEqual(result['opening_delta'],1)
        self.assertEqual(self.payload(result['comparison'])['expanded_coverage'][1]['sources'],['new-owned'])
        new=self.protocol(source='new-owned')
        result=compare(self.store,self.cohort([p,new])); self.assertIsNone(result['opening_delta'])

    def test_outage_partial_stale_and_protocol_change_prevent_comparison(self):
        for mode in ('failed','partial','stale','changed'):
            with self.subTest(mode=mode):
                self.store=Store(Path(self.temp.name)/mode,clock=lambda:self.now); p=self.protocol()
                for d in range(4):
                    if d==2: self.capture(d,protocol=p,ids=() if mode=='failed' else ('req-1',),
                         complete=mode if mode in ('failed','partial') else 'complete-request',fresh=mode!='stale',changes=['collector changed'] if mode=='changed' else [])
                    else:self.capture(d,protocol=p)
                self.assertIsNone(compare(self.store,self.cohort([p]))['opening_delta'])

    def test_unassessed_changed_query_cannot_be_silently_dropped(self):
        p,_=self.populated(); self.capture(2,query='new query',ids=('changed-query',))
        self.assertIsNone(compare(self.store,self.cohort([p]))['opening_delta'])

    def test_withdrawal_removes_old_report_and_new_comparison_is_insufficient(self):
        p,captures=self.populated(); cohort=self.cohort([p]); result=compare(self.store,cohort)
        self.store.withdraw(captures[0]['observations'][0])
        with self.store.transaction() as s:self.assertNotIn(result['comparison'],s['artifacts'])
        self.assertIsNone(compare(self.store,cohort)['opening_delta'])

    def test_missing_publication_dates_are_not_discovery_dates(self):
        p,captures=self.populated()
        # Owned records have unknown publication date in the baseline fixture.
        result=compare(self.store,self.cohort([p],'publication'))
        self.assertIsNone(result['opening_delta'])

    def test_missing_and_duplicate_cadence_slots_fail_closed(self):
        p=self.protocol()
        for day in (0,1,3):self.capture(day,protocol=p)
        self.assertIsNone(compare(self.store,self.cohort([p]))['opening_delta'])

    def test_segment_review_preserves_original_and_multicountry_denominator(self):
        obs=self.capture(0,description='Work from Germany or India. Deutsch erforderlich.')['observations'][0]
        review={'schema_version':1,'observation':obs,'reviewer':'fixture','reviewed_at':self.now.isoformat(),
                'values':{'countries':['DE','IN'],'language':'de'},
                'evidence':{'countries':{'source_field':'description','quote':'Germany or India','reason':'Explicit locations'},
                            'language':{'source_field':'description','quote':'Deutsch erforderlich.','reason':'Owned snippet language review'}},
                'limitations':['Fixture assertions only.'],'supersedes':None}
        key=review_segments(self.store,review)['segments']; before=self.payload(obs)
        result=coverage(self.store); self.assertEqual(result['counts']['deduplicated_openings'],1)
        self.assertEqual(result['segments']['countries'],{'DE':1,'IN':1})
        self.assertEqual(self.payload(obs),before)
        bad=deepcopy(review);bad['supersedes']=key;bad['evidence']['language']['source_field']='title'
        with self.assertRaises(EvidenceError):review_segments(self.store,bad)
        self.store.withdraw(obs)
        with self.store.transaction() as s:self.assertNotIn(key,s['artifacts'])

    def test_reviewed_board_mapping_retains_scope_and_requisition_evidence(self):
        result=self.capture(0); obs=result['observations'][0]
        ctx=import_context(self.store,context_bundle('product',content='Employer example.com owns the owned board.'))['contexts'][0]
        board=register_board(self.store,{'schema_version':1,'source':'synthetic-owned','instance':'owned','board':'owned',
              'employer_domain':'example.com','ownership_context':ctx,'quote':'example.com owns the owned board',
              'reviewer':'fixture','limitations':['Owned board ownership fixture.']})['board']
        link=link_board(self.store,{'schema_version':1,'observation':obs,'board':board,'source_field':'url',
                        'quote':'req-1','employer_requisition':'req-1','reviewer':'fixture'})['link']
        r=coverage(self.store);self.assertEqual(r['counts']['distinct_verified_employer_domains'],1)
        self.store.withdraw(ctx)
        with self.store.transaction() as s:self.assertNotIn(link,s['artifacts']);self.assertNotIn(r['coverage'],s['artifacts'])

    def test_two_board_absences_24_hours_apart_close_but_feed_does_not(self):
        for scope,expected in [('board-inventory','no-longer-listed'),('bounded-sample','stale')]:
            self.store=Store(Path(self.temp.name)/scope,clock=lambda:self.now);p=self.protocol(scope=scope)
            self.capture(0,protocol=p);self.capture(1,protocol=p,ids=());self.capture(2,protocol=p,ids=())
            result=vacancy_view(self.store,p);self.assertEqual(result['statuses'],{expected:1})

    def test_outage_and_single_absence_do_not_close(self):
        p=self.protocol(scope='board-inventory');self.capture(0,protocol=p)
        self.capture(1,protocol=p,ids=(),complete='failed');self.capture(2,protocol=p,ids=())
        self.assertNotIn('no-longer-listed',vacancy_view(self.store,p)['statuses'])

    def translation_worker(self,output,callback=lambda:None):
        class Worker:
            def __init__(self,*a):pass
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def run(self,*a):callback();return deepcopy(output),{'fixture':True}
        return Worker

    def translation_setup(self):
        data=bundle();data['policy'].update(hosted_disclosure=True,hosted_retention='provider-managed-no-deletion-deadline',hosted_permission_reference='owned')
        obs=self.store.import_bundle(data)['observations'][0]
        with self.store.transaction() as s:q=self.store.put(s,'runtime-qualification',{'owned':True})
        patcher=patch('tools.research_languages.qualified',return_value=(q,{'owned':True}));patcher.start();self.addCleanup(patcher.stop)
        return obs

    def test_translation_cache_review_and_original_remain_separate(self):
        obs=self.translation_setup();output={'segments':[{'index':0,'translated':'Owned translation fixture.'}],'limitations':['Not human quality measured.']}
        first=translate(self.store,obs,'de',worker_factory=self.translation_worker(output))
        self.assertEqual(first['proposal'],translate(self.store,obs,'de',worker_factory=self.translation_worker(output))['proposal'])
        self.assertEqual(self.payload(obs)['description'],BODY)
        review_translation(self.store,{'schema_version':1,'proposal':first['proposal'],'decision':'reject','reviewer':'fixture','notes':'Fictional source label; reject.'})
        self.assertEqual(self.payload(coverage(self.store)['coverage'])['translated_observations'],0)
        self.store.withdraw(obs)
        with self.store.transaction() as s:self.assertNotIn(first['proposal'],s['artifacts'])

    def test_translation_omission_and_midrun_withdrawal_fail(self):
        obs=self.translation_setup();output={'segments':[{'index':1,'translated':'Incomplete.'}],'limitations':['Fixture']}
        with self.assertRaises(EvidenceError):translate(self.store,obs,'de',worker_factory=self.translation_worker(output))
        output['segments'][0]['index']=0
        with self.assertRaises(EvidenceError):translate(self.store,obs,'de',worker_factory=self.translation_worker(output,lambda:self.store.withdraw(obs)))

    def test_language_evaluation_versions_labels_and_duplicate_control(self):
        obs=self.capture(0)['observations'][0];gold_annotation=annotation(obs);gold_annotation['reviewed_at']=self.now.isoformat()
        gold=freeze_gold(self.store,{'schema_version':1,'language':'de','split':'held-out','annotation':gold_annotation,'limitations':['Synthetic labels, not human review.']})['gold']
        self.now+=timedelta(seconds=1);actual=deepcopy(gold_annotation);actual['reviewed_at']=self.now.isoformat()
        analysis=self.store.annotate(actual)['analysis'];pairs=[{'gold':gold,'analysis':analysis}]
        result=evaluate_languages(self.store,pairs);group=next(iter(result['by_language_version'].values()))
        self.assertEqual(group['true_positive'],1);self.assertEqual(group['held_out_examples'],1)
        self.assertEqual(result['promotion'],'requires_human_review_no_automatic_language_promotion')
        with self.assertRaises(EvidenceError):evaluate_languages(self.store,pairs*2)
        self.store.withdraw(obs)
        with self.store.transaction() as s:self.assertNotIn(result['evaluation'],s['artifacts'])

    def test_wrong_sampling_time_is_insufficient(self):
        p=self.protocol(capture_offset_seconds=0)
        for d in range(4): self.capture(d,protocol=p)
        result=compare(self.store,self.cohort([p]))
        self.assertIsNone(result['opening_delta'])
        self.assertTrue(any('timing' in s for s in result['issues']))

    def test_model_version_changes_block_capability_deltas(self):
        p,captures=self.populated()
        for day,capture in enumerate(captures):
            for obs in capture['observations']:
                a=annotation(obs);a['reviewed_at']=self.now.isoformat()
                with self.store.transaction() as state:
                    execution=self.store.put(state,'execution',{'versions':{'owned-model':'v1' if day<2 else 'v2'}},[obs])
                    self.store.put(state,'analysis',{**a,'method':'codex-extraction','ai_domain':'in-domain','execution':execution},[obs,execution])
        result=compare(self.store,self.cohort([p]));payload=self.payload(result['comparison'])
        self.assertEqual(result['status'],'comparable-sample')
        self.assertIsNone(payload['capability_deltas'])
        self.assertNotEqual(payload['windows'][0]['analysis_versions'],payload['windows'][1]['analysis_versions'])

    def test_source_segment_lists_remain_visible_without_inflating_openings(self):
        data=bundle();data['observations'][0]['segments']['employment_type']=['Full-Time','Contract']
        self.store.import_bundle(data);r=coverage(self.store)
        self.assertEqual(r['segments']['employment_type'],{'Contract':1,'Full-Time':1})
        self.assertEqual(r['counts']['deduplicated_openings'],1)

    def test_deterministic_translation_chunks_preserve_whitespace_and_empty_model_limits(self):
        from tools.research_languages import source_segments, validate_translation
        body='A'*1700+'\n\n'+'B'*1800+'\n'
        chunks=source_segments(body)
        result=validate_translation({'segments':[{'index':i,'translated':'Owned translation'} for i,_ in enumerate(chunks)],'limitations':[]},body)
        self.assertEqual(''.join(r['original'] for r in result['segments']),body)
        self.assertEqual(result['segments'][-1]['end'],len(body));self.assertTrue(result['limitations'])

    def test_translation_acceptance_changes_only_reviewed_translation_coverage(self):
        obs=self.translation_setup();output={'segments':[{'index':0,'translated':'Owned translation.'}],'limitations':[]}
        p=translate(self.store,obs,'de',worker_factory=self.translation_worker(output))['proposal']
        before=self.store.snapshot()
        review_translation(self.store,{'schema_version':1,'proposal':p,'decision':'accept','reviewer':'synthetic reviewer','notes':'Owned test only; no human language-quality claim.'})
        self.assertEqual(self.payload(coverage(self.store)['coverage'])['translated_observations'],1)
        self.assertEqual(self.store.snapshot(),before)


    def test_multilingual_fixture_labels_resolve_to_original_source_spans(self):
        data=json.loads((Path(__file__).parent/'fixtures/research/multilingual-v1.json').read_text())
        self.assertEqual({e['language'] for e in data['examples']},{'en','de','hi','es'})
        self.assertEqual(data['human_review'],'pending')
        for example in data['examples']:
            obs=self.capture(0,ids=(example['id'],),description=example['description'])['observations'][0]
            labels=annotation(obs);labels.update(reviewed_at=self.now.isoformat(),responsibility_class=example['responsibility_class'],claims=example['claims'])
            frozen=freeze_gold(self.store,{'schema_version':1,'language':example['language'],'split':'held-out','annotation':labels,'limitations':data['limitations']})
            self.assertIn('gold',frozen)

    def test_review_display_preserves_languages_without_terminal_controls(self):
        from tools.research_global import display_json
        value={'text':'मूल्यांकन \x1b[31m \u202e'}
        rendered=display_json(value)
        self.assertIn('मूल्यांकन',rendered)
        self.assertNotIn('\x1b',rendered);self.assertNotIn('\u202e',rendered)
        self.assertEqual(json.loads(rendered),value)

    def test_board_instance_collision_requires_distinct_source_identity(self):
        self.protocol()
        with self.assertRaises(EvidenceError):self.protocol(instance='eu',board='different-employer')
        self.assertTrue(self.protocol(source='synthetic-owned:eu:different-employer',instance='eu',board='different-employer'))


if __name__=='__main__':unittest.main()
