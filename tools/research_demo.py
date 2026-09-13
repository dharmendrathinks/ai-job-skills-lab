"""Offline presentation fixture; never creates a research store or qualification.

All annotations and proposals here are author-written examples. The production
renderer receives an in-memory fixture, not imported model results. No network,
credentials, runtime authentication, application setup or private state is used.
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile

from tools.research_evidence import ROOT, aggregate, digest
from tools.research_analysis import normalize_output
from tools.research_skills import skill_payload
from tools.research_reports import render

NOTICE = 'SYNTHETIC OFFLINE DEMO — fictional jobs and author-written drafts; no model inference, market demand or completed work.'


def demo_state(now):
    from tools.research_curricula import curriculum_payload
    from tools.research_skills import catalog, history_payload
    state = {'schema_version':1,'artifacts':{},'withdrawn':[]}
    def put(kind,payload,dependencies=()):
        row={'schema_version':1,'kind':kind,'payload':payload,'dependencies':sorted(dependencies),'use_until':None}
        key=digest(row);state['artifacts'][key]=row;return key
    fixture=json.loads((ROOT/'examples/offline-demo.json').read_text())['bundle']
    cat={s['id']:s for s in catalog()['skills']}
    bundles=[['python','pydantic','structured-output','llm-evaluation'],
        ['python','rag','embeddings','retrieval-evaluation'],['python','tool-calling','observability','prompt-injection'],
        ['typescript','json-schema','llms'],['aws','docker','opentelemetry'],['sql','postgresql','data-pipelines']]
    # Two owned synthetic windows; no real collection, employer or quality claim.
    for age in (40,2):
        captured=(now-timedelta(days=age)).isoformat()
        policy=put('policy',{**fixture['policy'],'reviewed_at':captured})
        receipt=put('receipt',{**fixture['receipt'],'started_at':captured,'finished_at':captured},[policy])
        for i in range(12):
            skill_ids=bundles[i%len(bundles)][:]
            if age==2 and i%2==0: skill_ids += ['tool-calling','evaluation-datasets']
            skill_ids=list(dict.fromkeys(skill_ids))
            words=[cat[k]['name'] for k in skill_ids]
            if i==0: words+=['context routing experiments']
            description='Owned synthetic role. Practise '+', '.join(words)+'.'
            row=fixture['observations'][0]
            observation=put('observation',{**row,'native_id':'demo-role-'+str(i),'employer_name':'Example team '+str(i+1),
                'employer_requisition':'demo-'+str(i),'title':('Applied AI Engineer' if i%2 else 'AI Product Developer')+' · fictional',
                'url':'https://example.com/jobs/demo-'+str(i),'schema_version':1,'source':fixture['policy']['source'],
                'captured_at':captured,'description':description,'description_sha256':digest(description),
                'source_revision':'demo-'+str(age)+'-'+str(i),'receipt':receipt},[receipt])
            mentions=[{'surface':cat[k]['name'],'quote':description,'section_context':'','kind':cat[k]['kind'],'modality':'unspecified'} for k in skill_ids]
            if i==0:mentions.append({'surface':'context routing experiments','quote':description,'section_context':'','kind':'practice','modality':'unspecified'})
            output={'ai_domain':'in-domain','responsibility_class':'applied','claims':[{'kind':'responsibility','modality':'unspecified',
                'quote':description,'capabilities':['ai-product-engineering'],'tools':[]}],'unknowns':[NOTICE],'skill_mentions':mentions}
            labels=normalize_output(output,observation,description,now)
            put('analysis',{**labels,'ai_domain':'in-domain','method':'synthetic-fixture','reviewer':'Author-written synthetic example'},[observation])
    skills,deps=skill_payload(state,now);sid=put('skill-snapshot',skills,deps)
    market,deps=aggregate(state);mid=put('snapshot',market,deps)
    payload=curriculum_payload('structured-output',snapshot_id=sid,snapshot=skills)
    payload.update(created_at=now.isoformat(),status='synthetic-example',market_snapshot=mid)
    payload['proposal']['limitations'].append(NOTICE)
    path=put('learning-path',payload,[sid,mid])
    put('learning-selection',{'schema_version':1,'path':path,'reviewer':'Fictional learner in the synthetic demo','selected_at':now.isoformat()},[path])
    events=[('schema','completed','Fictional example: defined six owned records and checked missing owners.'),
        ('integration','failure','Fictional example: a malformed JSON response was rejected; transport integration still needs work.')]
    for milestone,event,summary in events:
        put('learning-progress',{'schema_version':1,'path':path,'milestone':milestone,'event':event,'basis':'self-reported',
            'summary':summary,'observer':'Synthetic learner','occurred_at':now.isoformat(),'recorded_at':now.isoformat(),
            'evidence':[],'conditions':[NOTICE],'capabilities':[],'result_quotes':[],'supersedes':None},[])
    for kind in ('project','youtube'):
        put('brief',{'kind':kind,'created_at':now.isoformat(),'learning_path':path,'status':'synthetic-example','notice':NOTICE,
            'proposal':{'title':('Demo project: ' if kind=='project' else 'Demo experiment: ')+payload['proposal']['title'],
                'disposition':'practice' if kind=='project' else 'experiment','capabilities':['ai-product-engineering'],
                'sections':{'Problem':payload['curriculum']['summary'],'Deliverable':payload['curriculum']['outcome'],
                    'Experiment':'Compare structural validation and supported field extraction on held-out owned notes.',
                    'Results':'No real results. Progress entries are fictional presentation examples.',
                    'Teaching question':payload['proposal']['teaching_question']},
                'market_claims':[],'context_claims':[],'alternatives':[],'limitations':[NOTICE]}},[path])
    history,deps=history_payload(state,now)
    # A clearly marked illustrative comparison, never passed off as a qualified cohort.
    windows=history['windows']; previous,current=windows
    changes=[]
    for skill in sorted(set(previous['skills'])|set(current['skills'])):
        a=previous['skills'].get(skill);b=current['skills'].get(skill)
        if any(s and s['normalization']=='unresolved' for s in (a,b)):continue
        counts=[v['openings'] if v else 0 for v in (a,b)]
        changes.append({'skill':skill,'name':(b or a)['name'],'previous':counts[0],'current':counts[1],
            'percentage_points':100*(counts[1]/current['counts']['in_domain_denominator']-counts[0]/previous['counts']['in_domain_denominator'])})
    changes.sort(key=lambda c:(-c['percentage_points'],c['name']))
    history.update(change_indicators=changes,status='SYNTHETIC comparison illustration — not a qualified real cohort',issues=[NOTICE],
        demo_unavailable_example='Unavailable example: a missing capture, partial feed or changed analysis revision suppresses all change indicators.',
        limitation=NOTICE)
    put('skill-history',history,deps)
    return state


def generate_demo(reports_root=None):
    # A fresh output directory prevents touching live reports or replaying a store.
    root = Path(reports_root) if reports_root is not None else ROOT / 'reports'
    if root.is_symlink(): raise ValueError('demo output root must not be a symlink')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = Path(tempfile.mkdtemp(prefix='demo-', dir=root))
    now = datetime.now(timezone.utc)
    pages, _, _ = render(demo_state(now), now.isoformat(), 1000)
    for name, html in pages.items():
        path = target / name
        with path.open('x', encoding='utf-8') as output:
            path.chmod(0o600)
            output.write(html.replace('<main>', '<main><p class="notice">' + NOTICE + '</p>', 1))
    return {name: str(target / name) for name in pages}


if __name__ == '__main__':
    print(NOTICE)
    print(json.dumps(generate_demo(), indent=2))
