"""Owned learn/build/teach scenarios. Fixtures do not establish real skill quality."""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.research_evidence import Store, EvidenceError
from tools.research_analysis import analyze, normalize_output
from tools.research_skills import snapshot, skill_payload, normalize_mentions, monthly, review_mapping
from tools.research_learning import propose_path, select_path, record_progress, progress_profile
from tools.research_questions import answer
from tools.research_context import import_context
from tools.research_operations import report, configure, execute, ledger
from tests.test_research_evidence import bundle, BODY
from tests.test_research_decisions import NOW, context_bundle


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.now = NOW
        self.store = Store(Path(self.tmp.name)/'private', clock=lambda:self.now)
        data = bundle(); data['policy'].update(hosted_disclosure=True, hosted_retention='provider-managed-no-deletion-deadline', hosted_permission_reference='owned fixture')
        self.obs = self.store.import_bundle(data)['observations'][0]
        with self.store.transaction() as state: self.qid = self.store.put(state, 'runtime-qualification', {'owned':True})
        for target in ('tools.research_analysis.qualified', 'tools.research_learning.qualified'):
            p = patch(target, return_value=(self.qid, {'owned':True}));p.start();self.addCleanup(p.stop)
        self.calls = 0; self.on_run = lambda:None; self.on_enter = lambda:None
        self.output = {'ai_domain':'in-domain', 'responsibility_class':'applied', 'claims':[
            {'kind':'skill','modality':'preferred','quote':'Python preferred.','capabilities':['ai-product-engineering'],'tools':['Python']}],
            'unknowns':[], 'skill_mentions':[{'surface':'Python','quote':'Python preferred.','section_context':'', 'kind':'technology','modality':'preferred'}]}
        owner = self
        class Worker:
            def __init__(self,*a): pass
            def __enter__(self): owner.on_enter();return self
            def __exit__(self,*a): pass
            def run(self,prompt,schema):
                owner.calls += 1;owner.prompt=prompt;owner.schema=schema;owner.on_run()
                return deepcopy(owner.output), {'authentication':'owned-test'}
        self.worker = Worker

    def analyse(self):
        return analyze(self.store,self.obs,skill_details=True,worker_factory=self.worker)['analysis']

    def skills(self):
        key = snapshot(self.store)['snapshot']
        with self.store.transaction() as state:return key, deepcopy(state['artifacts'][key]['payload'])

    def path(self):
        self.analyse(); snap, data = self.skills()
        self.output = {'title':'Practise Python application boundaries','experiment':'A typed parser under malformed input',
            'why_now':'Illustrative owned learning fixture; not real demand.', 'disposition':'propose','skills':['python'],
            'prerequisites':['Check basic programming knowledge.'],'assumptions':['10–15 hours weekly assumed.'],
            'market_evidence': list(data['evidence']), 'teaching_question':'What fails on malformed input?',
            'milestones':[{'id':'build','title':'Build and inspect a parser','understand':'Validation boundaries',
                'implement':'An owned parser','self_check':'Explain one failure','artifact':'Owned test fixture',
                'tests':'Test malformed and valid inputs','resources':[],'hours_min':2,'hours_max':4,
                'demonstrates':'Only observed parser behaviour','does_not_demonstrate':'Production readiness'}],
            'limitations':['No human usefulness review; resources need inspection.']}
        return propose_path(self.store,snap,['python'],worker_factory=self.worker)['learning-path']

    def progress(self,key,basis='self-reported',**changes):
        policy = bundle()['policy']
        return {'schema_version':1,'path':key,'milestone':'build','event':'attempt','basis':basis,
            'summary':'I attempted an owned parser.','observer':'fixture author','occurred_at':self.now.isoformat(),
            'evidence':[],'conditions':[],'capabilities':[],'result_quotes':[],'supersedes':None,'policy':policy,**changes}

    def test_detailed_contract_preserves_v1_and_normalizes_exact_aliases(self):
        aid=self.analyse()
        with self.store.transaction() as state:
            a=state['artifacts'][aid]['payload'];self.assertEqual(a['schema_version'],2)
            self.assertEqual(a['skill_mentions'][0]['skill_id'],'python')
        out=deepcopy(self.output);out.pop('skill_mentions')
        self.assertEqual(normalize_output(out,'owned',BODY,self.now)['schema_version'],1)
        mentions=normalize_mentions([{'surface':'python','quote':'python','section_context':'','kind':'technology','modality':'unspecified'}],'python')
        self.assertEqual(mentions[0]['skill_id'],'python')

    def test_bad_spans_categories_or_contract_do_not_commit(self):
        for bad in ('quote','surface','section_context'):
            output=deepcopy(self.output);output['skill_mentions'][0][bad]='invented'
            with self.assertRaises(EvidenceError):normalize_output(output,'owned',BODY,self.now)
        m={'surface':'RSU','quote':'RSU','section_context':'','kind':'technology','modality':'unspecified'}
        with self.assertRaises(EvidenceError):normalize_mentions([m],'RSU')
        m['kind']='other-requirement';self.assertEqual(normalize_mentions([m],'RSU')[0]['kind'],'other-requirement')
        self.output.pop('skill_mentions')
        with self.assertRaises(EvidenceError):self.analyse()
        self.assertNotIn('analysis',self.store.status()['counts'])

    def test_dedup_denominators_pending_and_modality_overlap(self):
        self.output['skill_mentions']*=2;self.analyse()
        self.store.import_bundle(bundle(native_id='pending'))
        _,data=self.skills()
        self.assertEqual(data['skills']['python']['openings'],1)
        self.assertEqual(data['skills']['python']['modalities']['preferred'],1)
        self.assertEqual(data['counts']['in_domain_denominator'],1)
        self.assertEqual(data['counts']['pending_or_legacy_openings'],1)
        self.assertEqual(data['skills']['python']['share'],1)

    def test_adjacent_and_other_requirements_do_not_enter_rankings(self):
        self.output['ai_domain']='adjacent';self.analyse()
        _,data=self.skills();self.assertEqual(data['skills'],{});self.assertEqual(data['counts']['analysed_openings'],1)

    def test_publication_dates_do_not_fallback_to_capture(self):
        self.analyse()
        with self.store.transaction() as state:
            p,_=skill_payload(state,self.now,basis='publication')
        self.assertEqual(p['skills'],{});self.assertEqual(p['counts']['missing_date_revisions'],1)

    def test_new_capture_does_not_replace_old_window(self):
        self.analyse();old_time=self.now
        data=bundle(); self.now+=timedelta(days=40)
        data['receipt'].update(started_at=(self.now-timedelta(minutes=2)).isoformat(),finished_at=self.now.isoformat())
        data['observations'][0].update(captured_at=(self.now-timedelta(minutes=1)).isoformat(),description='New text.',source_revision='new')
        self.store.import_bundle(data)
        with self.store.transaction() as state:old,_=skill_payload(state,self.now,end=old_time)
        self.assertEqual(old['skills']['python']['openings'],1)

    def test_path_citation_survives_newer_job_revision_without_extra_opening(self):
        self.path();self.now+=timedelta(days=1)
        data=bundle()
        data['receipt'].update(started_at=(self.now-timedelta(minutes=2)).isoformat(),finished_at=self.now.isoformat())
        data['observations'][0].update(captured_at=(self.now-timedelta(minutes=1)).isoformat(),description='New retained description.',source_revision='new')
        self.store.import_bundle(data)
        result=report(self.store)
        html=Path(result['jobs']['path']).read_text()
        self.assertIn('id="observation-'+self.obs+'"',html)
        self.assertIn('Cited description outside the displayed jobs list',html)
        self.assertEqual(result['jobs']['total'],1)

    def test_window_and_responsibility_filter(self):
        self.analyse()
        with self.store.transaction() as state:
            p,_=skill_payload(state,self.now,responsibility='research-heavy')
            self.assertEqual(p['counts']['in_domain_denominator'],0)
            with self.assertRaises(EvidenceError):skill_payload(state,self.now,days=0)

    def test_count_answer_uses_full_snapshot_not_retrieval(self):
        self.analyse();snap,p=self.skills();calls=self.calls
        result=answer(self.store,snap,'How often is Python requested?')
        self.assertEqual(result['metrics']['python']['openings'],p['skills']['python']['openings'])
        self.assertEqual(self.calls,calls)
        self.assertEqual(answer(self.store,snap,'How often is COBOL requested?')['status'],'insufficient-evidence')

    def test_explanation_citations_and_numeric_guard(self):
        self.analyse();snap,p=self.skills();eid=next(iter(p['evidence']))
        self.output={'statements':[{'explanation':'Python is explicitly preferred.','evidence':[eid]}], 'limitations':['Owned example only.']}
        result=answer(self.store,snap,'What does Python work involve?',worker_factory=self.worker)
        with self.store.transaction() as state:self.assertIn(eid,state['artifacts'][result['evidence-answer']]['payload']['citations'])
        self.output['statements'][0]['explanation']='99 percent of jobs require it.'
        with self.assertRaises(EvidenceError):answer(self.store,snap,'Explain Python requirements differently.',worker_factory=self.worker)

    def test_model_intent_prevents_automatic_ambiguous_retry(self):
        self.analyse();snap,_=self.skills()
        self.output={}
        with self.assertRaises(EvidenceError):answer(self.store,snap,'Explain Python.',worker_factory=self.worker)
        calls=self.calls
        with self.assertRaises(EvidenceError):answer(self.store,snap,'Explain Python.',worker_factory=self.worker)
        self.assertEqual(self.calls,calls)
        with self.store.transaction() as state:
            failures=[k for k,a in state['artifacts'].items() if a['kind']=='learning-failure']
        self.assertEqual(len(failures),1)
        self.store.withdraw(self.obs)
        with self.store.transaction() as state:self.assertNotIn(failures[0],state['artifacts'])

    def test_abstained_path_does_not_invent_milestones_or_completion(self):
        from tools.research_learning import validate_path
        key=self.path()
        with self.store.transaction() as state:
            data=state['artifacts'][state['artifacts'][key]['dependencies'][0]]['payload']['input']
            proposal=deepcopy(state['artifacts'][key]['payload']['proposal'])
            proposal.update(disposition='insufficient-evidence',milestones=[])
            p=validate_path(proposal,data)
            abstained=self.store.put(state,'learning-path',{'created_at':self.now.isoformat(),**p},[key])
        with self.assertRaises(EvidenceError):select_path(self.store,abstained,'fixture reviewer')
        html=Path(report(self.store)['path']).read_text()
        self.assertIn('Insufficient evidence for a path',html)
        self.assertNotIn('All milestones explicitly recorded complete',html)

    def test_path_select_and_report_tabs(self):
        key=self.path();select_path(self.store,key,'fixture author')
        html=Path(report(self.store)['path']).read_text()
        for name in ('path','skill','project','youtube','progress'):self.assertIn('data-tab="'+name+'"',html)
        self.assertIn('ACTIVE LEARNING PATH',html);self.assertIn('Python',html)
        self.assertIn('No progress recorded',html)

    def test_resource_contract_reuses_context_import(self):
        data=context_bundle('learning-resource',content='Owned parser documentation.')
        key=import_context(self.store,data)['contexts'][0]
        with self.store.transaction() as state:self.assertEqual(state['artifacts'][key]['payload']['evidence_type'],'learning-resource')

    def test_path_abstains_on_uninspected_resource(self):
        key=self.path()
        self.output['milestones'][0]['resources']=['invented-resource']
        with self.store.transaction() as state:p=state['artifacts'][key]['payload']
        # Different question input/context is unnecessary: direct validation checks the contract.
        from tools.research_learning import validate_path
        _,snap=self.skills()
        data={'skills':snap['skills'],'evidence':snap['evidence'],'resources':{}}
        with self.assertRaises(EvidenceError):validate_path(self.output,data)

    def test_progress_survives_job_withdrawal_but_market_path_does_not(self):
        path=self.path();key=record_progress(self.store,self.progress(path))['progress']
        result=report(self.store);self.store.withdraw(self.obs)
        self.assertFalse(Path(result['path']).exists())
        with self.store.transaction() as state:
            self.assertNotIn(path,state['artifacts']);self.assertIn(key,state['artifacts'])
        html=Path(report(self.store)['path']).read_text();self.assertIn('Market justification unavailable',html)

    def test_observed_progress_requires_reproduced_result_and_conditions(self):
        path=self.path()
        with self.assertRaises(EvidenceError):record_progress(self.store,self.progress(path,basis='observed'))
        key=record_progress(self.store,self.progress(path))['progress']
        with self.assertRaises(EvidenceError):progress_profile(self.store,key)

    def test_failure_correction_and_scoped_profile_proposal(self):
        path=self.path()
        fail=record_progress(self.store,self.progress(path,event='failure',summary='Owned test failed.'))['progress']
        data=context_bundle('experiment-result',content='Owned parser test passed.')
        data['records'][0].update(observation_basis='reproduced',conditions=['Owned fixture on test runtime.'])
        cid=import_context(self.store,data)['contexts'][0]
        row=self.progress(path,basis='observed',event='correction',summary='Owned parser corrected.',supersedes=fail,
                          evidence=[cid],conditions=['Owned fixture on test runtime.'],capabilities=['ai-product-engineering'],result_quotes=['Owned parser test passed.'])
        key=record_progress(self.store,row)['progress'];proposal=progress_profile(self.store,key)
        self.assertEqual(proposal['status'],'pending-human-review')
        self.assertNotIn('research-profile',self.store.status()['counts'])
        self.store.withdraw(cid)
        with self.store.transaction() as state:self.assertNotIn(proposal['proposal'],state['artifacts'])

    def test_partial_months_never_become_growth(self):
        self.analyse();h=monthly(self.store)
        with self.store.transaction() as state:
            p=state['artifacts'][h['history']]['payload']
            self.assertIsNone(p['change_indicators']);self.assertEqual(len(p['windows']),2)

    def test_completed_is_explicit_and_corrected_profile_is_retracted(self):
        from tools.research_profile import review
        path=self.path()
        data=context_bundle('experiment-result',content='Owned parser test passed.')
        data['records'][0].update(observation_basis='reproduced',conditions=['Owned test runtime.'])
        cid=import_context(self.store,data)['contexts'][0]
        own=context_bundle()['policy']
        row=self.progress(path,basis='observed',event='test',evidence=[cid],conditions=['Owned test runtime.'],
                          capabilities=['ai-product-engineering'],result_quotes=['Owned parser test passed.'],policy=own)
        first=record_progress(self.store,row)['progress']
        proposal=progress_profile(self.store,first)['proposal']
        profile=review(self.store,proposal,'accept','owned fixture reviewer')['profile']
        html=Path(report(self.store)['path']).read_text()
        self.assertNotIn('All milestones explicitly recorded complete',html)
        self.now+=timedelta(seconds=1)
        corrected=record_progress(self.store,{**row,'event':'correction','supersedes':first,
                  'summary':'Correction: this result does not demonstrate the capability.','capabilities':[]})['progress']
        with self.store.transaction() as state:self.assertNotIn(profile,state['artifacts'])
        self.now+=timedelta(seconds=1)
        record_progress(self.store,self.progress(path,event='completed',summary='Fixture author completed this bounded exercise.'))
        self.assertIn('All milestones explicitly recorded complete',Path(report(self.store)['path']).read_text())

    def test_linked_teaching_receives_observed_work_and_same_experiment(self):
        import json
        from tools.research_briefs import generate, SECTIONS, DIMENSIONS
        path=self.path()
        with self.store.transaction() as state:
            p=deepcopy(state['artifacts'][path]['payload'])
            analysis=next(a for a in state['artifacts'] if state['artifacts'][a]['kind']=='analysis')
        data=context_bundle('experiment-result',content='Owned parser test passed.')
        data['records'][0].update(observation_basis='reproduced',conditions=['Owned fixture runtime.'])
        cid=import_context(self.store,data)['contexts'][0]
        progress=record_progress(self.store,self.progress(path,basis='observed',event='test',evidence=[cid],
            conditions=['Owned fixture runtime.'],result_quotes=['Owned parser test passed.'],policy=context_bundle()['policy']))['progress']
        self.output={'title':'Explain the owned parser experiment','disposition':'propose',
            'capabilities':['ai-product-engineering'],'prerequisites':[],
            'market_claims':[{'analysis':analysis,'quote':'Python preferred.'}],
            'context_claims':[{'context':cid,'quote':'Owned parser test passed.','relation':'supports'}],
            'alternatives':[],'sections':{name:'Owned fixture; explain the bounded experiment.' for name in SECTIONS['youtube']},
            'judgments':{name:{'rating':'unknown','reason':'No external demand evidence.'} for name in DIMENSIONS},
            'limitations':['Owned fixture only.']}
        with patch('tools.research_briefs.qualified',return_value=(self.qid,{'owned':True})):
            result=generate(self.store,'youtube',p['market_snapshot'],p['contexts'],learning_path=path,worker_factory=self.worker)
        supplied=json.loads(self.prompt.split('\nUntrusted evidence JSON:\n')[1])
        self.assertEqual(supplied['learning_path']['proposal']['experiment'],p['proposal']['experiment'])
        self.assertIn(progress,supplied['learning_progress']);self.assertIn(cid,supplied['contexts'])
        with self.store.transaction() as state:self.assertEqual(state['artifacts'][result['brief']]['payload']['learning_path'],path)

    def test_linked_pair_resumes_only_failed_half_after_explicit_review(self):
        from tools.research_learning import path_briefs
        path=self.path();calls=[]
        def generate(store,kind,*args,**kwargs):
            calls.append(kind)
            if calls==['project','youtube']:raise EvidenceError('owned timeout')
            with store.transaction() as state:
                execution=store.put(state,'brief-execution',{'kind':kind,'recorded_at':self.now.isoformat()},[path])
                key=store.put(state,'brief',{'kind':kind,'learning_path':path,'execution':execution},[execution])
            return {'brief':key,'cache_hit':False}
        with patch('tools.research_briefs.generate',side_effect=generate):
            with self.assertRaises(EvidenceError):path_briefs(self.store,path)
            with self.assertRaises(EvidenceError):path_briefs(self.store,path)
            self.assertEqual(calls,['project','youtube'])
            result=path_briefs(self.store,path,retry_review='Fixture reviewer inspected the unfinished attempt.')
            self.assertTrue(result['project']['cache_hit']);self.assertFalse(result['youtube']['cache_hit'])
            self.assertEqual(calls,['project','youtube','youtube'])
            self.assertTrue(path_briefs(self.store,path)['youtube']['cache_hit'])

    def test_retry_rebuilds_views_without_repeating_completed_external_steps(self):
        from tools.research_operations import resolve_step, save_ledger
        plan=configure(self.store,{'schema_version':1,'collect':None,'analyze':True,'skill_details':True,'brief_kinds':[],
             'contexts':[],'profile':None,'analysis_limit':1,'report_limit':20,'backup':False,'interval_seconds':3600,'reviewer':'fixture'})['plan']
        with patch('tools.research_analysis.analyze',side_effect=EvidenceError('owned failure')):
            run=execute(self.store,plan)['run']
        log=ledger(self.store)
        self.assertIn('report',log['runs'][run]['steps'])
        log['runs'][run]['steps']['brief:youtube']={'status':'done','ids':[]};save_ledger(self.store,log)
        resolve_step(self.store,run,'analyze:'+self.obs,'retry','fixture operator','Inspected owned failure; explicit test retry.')
        steps=ledger(self.store)['runs'][run]['steps']
        self.assertNotIn('report',steps);self.assertNotIn('skills-snapshot',steps)
        self.assertEqual(steps['brief:youtube']['status'],'done')

    def test_withdrawal_during_generation_blocks_path(self):
        self.on_run=lambda:self.store.withdraw(self.obs)
        with self.assertRaises(EvidenceError):self.path()

    def test_mapping_requires_inspected_matching_kind(self):
        aid=self.analyse()
        with self.assertRaises(EvidenceError):review_mapping(self.store,{'schema_version':1,'from_id':'invented','to_id':'python','analyses':[aid],'reviewer':'fixture','reason':'fixture'})

    def test_skill_refresh_uses_latest_observations_and_reports_overflow(self):
        plan=configure(self.store,{'schema_version':1,'collect':None,'analyze':True,'skill_details':True,'brief_kinds':[],
             'contexts':[],'profile':None,'analysis_limit':1,'report_limit':20,'backup':False,'interval_seconds':3600,'reviewer':'fixture'})['plan']
        self.store.import_bundle(bundle(native_id='pending'))
        with patch('tools.research_analysis.analyze',return_value={}) as model:
            execute(self.store,plan)
            self.assertTrue(model.call_args.kwargs['skill_details'])
            self.assertEqual(model.call_count,1)
        self.assertEqual(next(iter(ledger(self.store)['runs'].values()))['overflow'],1)

    def test_rejected_path_is_not_recommended_under_same_skills(self):
        from tools.research_learning import path_decision
        key=self.path()
        path_decision(self.store,{'schema_version':1,'path':key,'decision':'rejected','reason':'Owned exercise not useful.',
                                 'reviewer':'fixture author','defer_until':None})
        with self.assertRaises(EvidenceError):select_path(self.store,key,'fixture author')
        with self.store.transaction() as state:p=state['artifacts'][key]['payload']
        with self.assertRaises(EvidenceError):propose_path(self.store,p['skill_snapshot'],['python'],worker_factory=self.worker)

    def test_baseline_uses_frozen_identical_inputs_and_is_not_a_recommendation(self):
        import json
        from tools.research_learning import compare_path
        key=self.path()
        original=json.loads(self.prompt.split('\nUntrusted input JSON:\n')[1])
        result=compare_path(self.store,key,worker_factory=self.worker)
        baseline=json.loads(self.prompt.split('\nUntrusted input JSON:\n')[1])
        self.assertEqual(original,baseline)
        self.assertIn('learning-comparison',result)
        self.assertEqual(self.store.status()['counts']['learning-path'],1)

    def test_provisional_evaluation_does_not_claim_human_acceptance(self):
        from tools.evaluate_skills import evaluate
        aid=self.analyse()
        row={'schema_version':1,'dataset_revision':'owned-test/1','label_basis':'provisional','reviewer':'fixture author',
             'examples':[{'analysis':aid,'split':'held-out','expected':[{'surface':'Python','kind':'technology','modality':'preferred'}]}]}
        result=evaluate(self.store,row)
        self.assertEqual(result['precision'],1);self.assertEqual(result['acceptance'],'requires-human-review')
        self.store.withdraw(self.obs)
        with self.store.transaction() as state:self.assertNotIn(result['evaluation'],state['artifacts'])

    def test_rejected_model_response_stays_in_policy_controlled_diagnostics(self):
        self.output['skill_mentions'][0]['surface']='not in quote'
        with self.assertRaises(EvidenceError):self.analyse()
        with self.store.transaction() as state:
            failed=[a for a in state['artifacts'].values() if a['kind']=='execution']
            self.assertEqual(failed[0]['payload']['failure_stage'],'normalization')
            self.assertEqual(failed[0]['payload']['response'],self.output)
        self.store.withdraw(self.obs)
        self.assertNotIn('execution',self.store.status()['counts'])

    def test_cross_source_copies_count_one_verified_opening(self):
        self.analyse()
        data=bundle('another-owned-source');data['policy'].update(hosted_disclosure=True,hosted_retention='provider-managed-no-deletion-deadline',hosted_permission_reference='owned')
        self.obs=self.store.import_bundle(data)['observations'][0];self.analyse()
        _,data=self.skills()
        self.assertEqual(data['skills']['python']['openings'],1)
        self.assertEqual(data['counts']['analysed_openings'],1)
        self.assertEqual(data['skills']['python']['verified_employers'],1)

    def test_kind_mapping_cannot_silently_turn_practice_into_technology(self):
        m={'surface':'Python','quote':'Python','section_context':'','kind':'practice','modality':'unspecified'}
        with self.assertRaises(EvidenceError):normalize_mentions([m],'Python')
