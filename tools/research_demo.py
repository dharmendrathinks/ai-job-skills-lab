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
    state = {'schema_version': 1, 'artifacts': {}, 'withdrawn': []}

    def put(kind, payload, dependencies=()):
        row = {'schema_version': 1, 'kind': kind, 'payload': payload,
               'dependencies': sorted(dependencies), 'use_until': None}
        key = digest(row); state['artifacts'][key] = row
        return key

    fixture = json.loads((ROOT / 'examples/offline-demo.json').read_text())['bundle']
    captured = (now - timedelta(hours=1)).isoformat()
    policy = put('policy', {**fixture['policy'], 'reviewed_at': captured})
    receipt = put('receipt', {**fixture['receipt'], 'started_at': captured, 'finished_at': captured}, [policy])
    row = fixture['observations'][0]
    observation = put('observation', {**row, 'schema_version': 1, 'source': fixture['policy']['source'],
        'captured_at': captured, 'description_sha256': digest(row['description']), 'receipt': receipt}, [receipt])
    output = {'ai_domain': 'in-domain', 'responsibility_class': 'applied',
        'claims': [{'kind': 'responsibility', 'modality': 'unspecified',
            'quote': 'Build retrieval pipelines in Python.', 'capabilities': ['retrieval-knowledge'], 'tools': ['Python']}],
        'unknowns': [NOTICE], 'skill_mentions': [{'surface': 'Python', 'quote': 'Build retrieval pipelines in Python.',
            'section_context': '', 'kind': 'technology', 'modality': 'unspecified'}]}
    labels = normalize_output(output, observation, row['description'], now)
    analysis = put('analysis', {**labels, 'ai_domain': 'in-domain', 'method': 'synthetic-fixture',
        'reviewer': 'Author-written offline presentation fixture; no model execution'}, [observation])
    skills, deps = skill_payload(state, now)
    sid = put('skill-snapshot', skills, deps)
    market, deps = aggregate(state)
    mid = put('snapshot', market, deps)
    path = put('learning-path', {'schema_version': 1, 'created_at': now.isoformat(),
        'status': 'synthetic-example', 'skill_snapshot': sid, 'market_snapshot': mid, 'contexts': [],
        'profile': None, 'selection_limits': [NOTICE], 'proposal': {
            'title': 'Demo: build a small retrieval evaluation harness', 'disposition': 'propose',
            'experiment': 'Compare a keyword baseline on ten author-owned questions, including missing answers.',
            'why_now': 'Illustrates the learn → build → teach workflow; not a real recommendation.',
            'skills': ['python'], 'prerequisites': ['Basic Python and test assertions'],
            'market_evidence': list(skills['evidence']), 'assumptions': ['Two to four hours; CPU only; no paid API.'],
            'teaching_question': 'When does a simple retrieval baseline fail?', 'limitations': [NOTICE],
            'milestones': [{'id': 'evaluate', 'title': 'Measure a baseline before changing it',
                'understand': 'Separate retrieval misses from unanswered questions.',
                'implement': 'Write a small Python scorer over documents you own.',
                'self_check': 'Can you explain a failed query without changing the held-out questions?',
                'artifact': 'A reusable test harness and a failure table.', 'tests': 'Known answer, missing answer and misleading match.',
                'resources': [], 'hours_min': 2, 'hours_max': 4,
                'demonstrates': 'Only results actually measured under recorded conditions.',
                'does_not_demonstrate': 'Production reliability or general mastery.'}]}}, [sid, mid])
    for kind, title, sections in [
        ('project', 'Demo project: inspect alternatives before starting', {
            'problem': 'Make retrieval failures visible while learning Python.',
            'alternatives': 'No repository inspected in this offline example; inspect contribution options first.',
            'bounded_deliverable': 'A small scorer, fixed questions and reproducible failure cases.',
            'tests': 'Compare exact-match baseline, missing-answer cases and held-out questions.'}),
        ('youtube', 'Demo experiment: where a retrieval baseline fails', {
            'story': 'Problem → baseline → held-out test → observed failure → fix → limitations.',
            'experiment': 'Use the same harness as the learning path; record actual outcomes before scripting results.',
            'audience_validation': 'No discussion evidence inspected. Audience demand remains unknown.'}),
    ]:
        put('brief', {'kind': kind, 'created_at': now.isoformat(), 'learning_path': path,
            'status': 'synthetic-example', 'notice': NOTICE, 'proposal': {
                'title': title, 'disposition': 'insufficient-evidence', 'capabilities': ['retrieval-knowledge'],
                'sections': sections, 'market_claims': [{'analysis': analysis, 'quote': 'Build retrieval pipelines in Python.'}],
                'context_claims': [], 'alternatives': [], 'limitations': [NOTICE]}}, [path])
    return state


def generate_demo(reports_root=None):
    # A fresh output directory prevents touching live reports or replaying a store.
    root = Path(reports_root) if reports_root is not None else ROOT / 'reports'
    if root.is_symlink(): raise ValueError('demo output root must not be a symlink')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = Path(tempfile.mkdtemp(prefix='demo-', dir=root))
    now = datetime.now(timezone.utc)
    pages, _, _ = render(demo_state(now), now.isoformat(), 20)
    for name, html in pages.items():
        path = target / name
        with path.open('x', encoding='utf-8') as output:
            path.chmod(0o600)
            output.write(html.replace('<main>', '<main><p class="notice">' + NOTICE + '</p>', 1))
    return {name: str(target / name) for name in pages}


if __name__ == '__main__':
    print(NOTICE)
    print(json.dumps(generate_demo(), indent=2))
