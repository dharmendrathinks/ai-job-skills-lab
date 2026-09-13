"""Owned content, lifecycle and evidence scenarios for the learning workspace."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.research_curricula import (library, topics, preferences, curriculum_payload, propose_curriculum,
                                     inspect_curriculum, validate_adaptation, safe_url)
from tools.research_demo import demo_state
from tools.research_evidence import Store, EvidenceError, digest
from tools.research_learning import select_path, path_briefs, path_decision
from tools.research_operations import report
from tools.research_reports import render
from tools.research_skills import skill_payload, history_payload, monthly
import tests.test_research_global as global_fixtures

NOW = datetime(2026,9,13,tzinfo=timezone.utc)


class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=Store(Path(self.tmp.name)/'private',clock=lambda:NOW)

    def populate(self):
        data=demo_state(NOW)
        with self.store.transaction() as state: state.update(deepcopy(data))
        return next(k for k,a in data['artifacts'].items() if a['kind']=='skill-snapshot')

    def payload(self,key):
        with self.store.transaction() as state:return deepcopy(state['artifacts'][key]['payload'])

    def test_library_is_offline_complete_and_examples_execute(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')), patch.object(Store,'transaction',side_effect=AssertionError('store forbidden')):
            book=library(); self.assertEqual(len(book['paths']),3)
            self.assertEqual(len(topics()['topics']),8)
            for path in [book['foundations'],*book['paths']]:
                namespace={'__name__':'curriculum_example'}
                for lesson in path['lessons']:
                    # These are our checked-in original examples, never downloaded code.
                    exec(compile(lesson['example'],'owned-example','exec'),namespace)
                    self.assertTrue(lesson['resources']);self.assertTrue(lesson['completion_check'])
            self.assertEqual(len(inspect_curriculum()),3)

    def test_invalid_resources_prerequisites_and_preferences_fail(self):
        from tools.research_curricula import validate_lessons
        book=library();lessons=deepcopy(book['paths'][0]['lessons'])
        lessons[0]['prerequisites']=[lessons[-1]['id']]
        with self.assertRaises(EvidenceError):validate_lessons(lessons,book['resources'])
        for value in ({'hours_per_week':[20,5]},{'hours_per_week':[True,4]},{'additional_spending_inr':1},{'unknown':3}):
            with self.assertRaises(EvidenceError):preferences(value)
        self.assertIn('Not specified',preferences()['hardware'])
        for url in ('javascript:alert(1)','https://user:password@example.org','https://example.org\n/','file:///private'):
            self.assertFalse(safe_url(url))

    def test_curriculum_only_path_has_no_model_or_market_dependency(self):
        with patch('tools.research_runtime.CodexWorker.__enter__',side_effect=AssertionError('model forbidden')):
            result=propose_curriculum(self.store,'structured-output')
            key=result['learning-path'];payload=self.payload(key)
            self.assertEqual(payload['schema_version'],2);self.assertIsNone(payload['market_snapshot'])
            self.assertEqual(payload['proposal']['market_evidence'],[])
            self.assertEqual(propose_curriculum(self.store,'structured-output')['learning-path'],key)
            select_path(self.store,key,'owned tester')
            briefs=path_briefs(self.store,key)
            self.assertEqual(set(briefs),{'project','youtube'})
            self.assertTrue(path_briefs(self.store,key)['project']['cache_hit'])
            pages=report(self.store)
            self.assertIn('ACTIVE LEARNING PATH',Path(pages['path']).read_text())
            self.assertEqual(self.payload(briefs['project']['brief'])['proposal']['market_claims'],[])

    def test_private_preferences_and_frozen_curriculum_survive_editorial_change(self):
        key=propose_curriculum(self.store,'document-assistant',preference_input={'hours_per_week':[3,5],'hardware':'Owned CPU test environment'})['learning-path']
        p=self.payload(key)
        self.assertEqual(p['preferences']['hours_per_week'],[3,5])
        original=p['curriculum']['lessons'][0]['title']
        data=library();data['paths'][1]['lessons'][0]['title']='Later editorial revision'
        with patch('tools.research_curricula.library',return_value=data):
            self.assertEqual(self.payload(key)['curriculum']['lessons'][0]['title'],original)

    def test_rejected_curriculum_cannot_be_regenerated_or_briefed(self):
        key=propose_curriculum(self.store,'structured-output')['learning-path']
        path_decision(self.store,{'schema_version':1,'path':key,'decision':'rejected','reason':'Owned fixture choice','reviewer':'fixture','defer_until':None})
        with self.assertRaises(EvidenceError):propose_curriculum(self.store,'structured-output')
        with self.assertRaises(EvidenceError):path_briefs(self.store,key)

    def test_curriculum_brief_rejection_is_respected_before_cache_reuse(self):
        from tools.research_outcomes import decide
        key=propose_curriculum(self.store,'structured-output')['learning-path']
        bid=path_briefs(self.store,key)['project']['brief']
        decide(self.store,{'schema_version':1,'brief':bid,'decision':'rejected',
            'reason':'Owned fixture review','reviewer':'fixture','decided_at':NOW.isoformat(),
            'defer_until':None,'target':None,'supersedes':None})
        with self.assertRaises(EvidenceError):path_briefs(self.store,key)

    def test_corrected_work_retracts_curriculum_briefs_and_report(self):
        from tools.research_learning import record_progress
        from tests.test_research_learning import bundle
        key=propose_curriculum(self.store,'structured-output')['learning-path']
        row={'schema_version':1,'path':key,'milestone':self.payload(key)['proposal']['milestones'][0]['id'],
            'event':'completed','basis':'self-reported','summary':'Owned fixture initially reported complete.',
            'observer':'fixture','occurred_at':NOW.isoformat(),'evidence':[],'conditions':[],
            'capabilities':[],'result_quotes':[],'supersedes':None,'policy':bundle()['policy']}
        old=record_progress(self.store,row)['progress']
        briefs=path_briefs(self.store,key)
        page=Path(report(self.store)['path'])
        record_progress(self.store,{**row,'event':'correction','supersedes':old,
            'summary':'Owned fixture correction: completion was not established.'})
        self.assertFalse(page.exists())
        with self.store.transaction() as state:
            for result in briefs.values():self.assertNotIn(result['brief'],state['artifacts'])
            self.assertIn(old,state['artifacts']);self.assertIn(key,state['artifacts'])
        revised=self.payload(path_briefs(self.store,key)['project']['brief'])
        self.assertIn('completion was not established',revised['proposal']['sections']['Actual work'])
        self.assertNotIn('initially reported complete',revised['proposal']['sections']['Actual work'])

    def test_model_adaptation_preserves_curriculum_and_withdrawal(self):
        sid=self.populate();book=library();curriculum=book['paths'][0]
        with self.store.transaction() as state:qid=self.store.put(state,'runtime-qualification',{'owned':True})
        owner=self
        class Worker:
            def __init__(self,*args):pass
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def run(self,prompt,schema):
                owner.assertIn('Untrusted input JSON:',prompt)
                return {'rationale':'Owned fixture relevance, not market demand.','project_context':'Use owned release notes.',
                    'lesson_emphasis':[{'lesson':m['id'],'emphasis':'Keep the original check and use owned notes.'} for m in curriculum['lessons']],
                    'evidence':[schema['properties']['evidence']['items']['enum'][0]],'limitations':['Owned model fixture; not real quality evidence.']},{}
        with patch('tools.research_learning.qualified',return_value=(qid,{'owned':True})), patch('tools.research_learning.hosted_eligible'):
            key=propose_curriculum(self.store,'structured-output',sid,worker_factory=Worker)['learning-path']
        payload=self.payload(key)
        self.assertIn('adaptation',payload)
        self.assertEqual(payload['curriculum']['lessons'],curriculum['lessons'])
        pages=report(self.store)
        self.store.withdraw(sid)
        with self.store.transaction() as state:self.assertNotIn(key,state['artifacts'])
        self.assertFalse(Path(pages['path']).exists())

    def test_adaptation_without_hosted_permission_never_invokes_worker(self):
        sid=self.populate()
        with patch('tools.research_runtime.CodexWorker.__enter__',side_effect=AssertionError('model forbidden')):
            with self.assertRaises(EvidenceError):propose_curriculum(self.store,'structured-output',sid)

    def test_adaptation_cannot_change_lesson_order_or_invent_citations(self):
        book=library();data={'curriculum':book['paths'][0],'evidence':{'owned':{}}}
        proposal={'rationale':'Owned','project_context':'Owned','lesson_emphasis':[
            {'lesson':m['id'],'emphasis':'Owned'} for m in data['curriculum']['lessons']], 'evidence':['owned'],'limitations':['Owned']}
        validate_adaptation(proposal,data)
        wrong=deepcopy(proposal);wrong['lesson_emphasis'].reverse()
        with self.assertRaises(EvidenceError):validate_adaptation(wrong,data)
        wrong=deepcopy(proposal);wrong['evidence']=['invented']
        with self.assertRaises(EvidenceError):validate_adaptation(wrong,data)

    def test_new_snapshot_projects_typed_aliases_without_mutating_originals(self):
        state=demo_state(NOW)
        for a in state['artifacts'].values():
            if a['kind']=='analysis':
                for mention in a['payload']['skill_mentions']:
                    if mention['skill_id']=='tool-calling':
                        mention.update(skill_id='unresolved-owned',normalization='unresolved',catalog_revision='old/1')
        before=deepcopy(state)
        snapshot,_=skill_payload(state,NOW)
        self.assertEqual(state,before)
        self.assertNotIn('unresolved-owned',snapshot['skills'])
        self.assertEqual(snapshot['skills']['tool-calling']['normalization'],'catalog-projection')
        self.assertLessEqual(snapshot['skills']['tool-calling']['openings'],snapshot['counts']['in_domain_denominator'])
        self.assertTrue(any(e['original_skill_id']=='unresolved-owned' for e in snapshot['evidence'].values()))

    def test_report_has_resolving_anchors_and_no_visible_opaque_instructions(self):
        pages,_,_=render(demo_state(NOW),NOW.isoformat(),1000)
        class Anchors(HTMLParser):
            def __init__(self):super().__init__();self.ids=[];self.links=[]
            def handle_starttag(self,tag,attrs):
                attrs=dict(attrs)
                if 'id' in attrs:self.ids.append(attrs['id'])
                if tag=='a':self.links.append(attrs.get('href',''))
        parsed={}
        for name,html in pages.items():
            parser=Anchors();parser.feed(html);parsed[name]=parser
            self.assertEqual(len(parser.ids),len(set(parser.ids)))
            self.assertNotIn('To practise this skill, ask Codex',html)
        for name,parser in parsed.items():
            for link in parser.links:
                if '#' in link and not link.startswith('http'):
                    dest,anchor=link.split('#',1);self.assertIn(anchor,parsed[dest or name].ids)
        html=pages['workspace.html']
        for text in ('Browse skills','Observed terms','Trends','data-copy','data-lesson','READ THIS SECTION','data-skill-view="terms"'):
            self.assertIn(text,html)
        # A small display budget must not link to briefs or paths omitted by it.
        limited,_,_=render(demo_state(NOW),NOW.isoformat(),1)
        parsed={}
        for name,html in limited.items():
            parser=Anchors();parser.feed(html);parsed[name]=parser
        for name,parser in parsed.items():
            for link in parser.links:
                if '#' in link and not link.startswith('http'):
                    dest,anchor=link.split('#',1);self.assertIn(anchor,parsed[dest or name].ids)

    def test_unqualified_windows_never_show_change_indicators(self):
        state=demo_state(NOW);result,_=history_payload(state,NOW)
        self.assertIsNone(result['change_indicators']);self.assertTrue(result['issues'])
        empty={'schema_version':1,'artifacts':{},'withdrawn':[]}
        result,_=history_payload(empty,NOW)
        self.assertIsNone(result['change_indicators'])


class SkillCohortTests(unittest.TestCase):
    def setUp(self):
        # Reuse the owned capture fixture without inheriting or duplicating its tests.
        self.fixture=global_fixtures.GlobalTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.store=self.fixture.store

    def detailed_captures(self):
        from tools.research_analysis import normalize_output
        protocol,captures=self.fixture.populated()
        for capture in captures:
            with self.store.transaction() as state:
                for oid in capture['observations']:
                    observation=state['artifacts'][oid]['payload'];description=observation['description']
                    output={'ai_domain':'in-domain','responsibility_class':'applied','claims':[], 'unknowns':[],
                        'skill_mentions':[{'surface':'Python','quote':'Python preferred.','section_context':'','kind':'technology','modality':'preferred'}]}
                    row=normalize_output(output,oid,description,self.fixture.now)
                    row.update(ai_domain='in-domain',method='synthetic-fixture')
                    self.store.put(state,'analysis',row,[oid])
        return protocol,captures

    def test_reviewed_cohort_computes_shares_and_withdrawal_retracts_history(self):
        protocol,captures=self.detailed_captures();cohort=self.fixture.cohort([protocol])
        result=monthly(self.store,cohort=cohort)
        payload=self.fixture.payload(result['history'])
        self.assertEqual(payload['status'],'comparable-within-sample',payload['issues'])
        self.assertEqual(payload['change_indicators'][0]['percentage_points'],0)
        self.assertEqual(payload['change_indicators'][0]['previous'],1)
        self.assertEqual(payload['change_indicators'][0]['current'],2)
        self.store.withdraw(captures[0]['observations'][0])
        with self.store.transaction() as state:self.assertNotIn(result['history'],state['artifacts'])
        self.assertEqual(monthly(self.store,cohort=cohort)['status'],'descriptive-observations-only')

    def test_changed_normalization_or_missing_analysis_blocks_deltas(self):
        protocol,captures=self.detailed_captures();cohort=self.fixture.cohort([protocol])
        old_observations=set(captures[0]['observations']+captures[1]['observations'])
        with self.store.transaction() as state:
            for aid,a in list(state['artifacts'].items()):
                if a['kind']=='analysis' and a['payload']['observation'] in old_observations:
                    row=deepcopy(a['payload'])
                    for mention in row['skill_mentions']:mention['catalog_revision']='older/1'
                    self.store.remove(state,[aid]);self.store.put(state,'analysis',row,a['dependencies'])
        payload=self.fixture.payload(monthly(self.store,cohort=cohort)['history'])
        self.assertIsNone(payload['change_indicators'])
        self.assertIn('Original normalization revisions differ between windows.',payload['issues'])


class WorkspaceInteractionTests(unittest.TestCase):
    def test_bundled_script_behaves_without_network_or_browser_persistence(self):
        import shutil
        node=shutil.which('node')
        if not node:self.skipTest('Node is needed for offline DOM behavior tests')
        root=Path(__file__).resolve().parents[1]
        result=subprocess.run([node,str(root/'tests/workspace_ui.cjs'),str(root/'tools/report_assets/workspace.js')],
                              text=True,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
