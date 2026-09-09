"""Explicit immutable domain workspaces; no global taxonomy mutation or new collectors."""
from copy import deepcopy
import json
from pathlib import Path
import re

from tools.research_evidence import TAXONOMY, ROOT, digest, fields, require, strings, text

PACKS = {'backend-platform': ROOT/'docs/research/domains/backend-platform-v1.json'}


def validate_pack(pack):
    fields(pack, ['schema_version', 'id', 'version', 'title', 'taxonomy', 'responsibilities',
                  'exclusions', 'aliases', 'prerequisites', 'queries', 'evaluation', 'limitations'])
    require(pack['schema_version'] == 1 and re.fullmatch('[a-z][a-z0-9-]{2,60}', pack['id']) and
            pack['id'] != 'ai-engineering' and re.fullmatch('[1-9][0-9]*', pack['version']), 'unsupported domain identity')
    text(pack['title'], 150)
    tax = pack['taxonomy']; fields(tax, ['version', 'capabilities'])
    require(tax['version'] == pack['id']+'/capabilities/'+pack['version'], 'taxonomy version must pin domain revision')
    strings(tax['capabilities'], 50)
    require(0 < len(tax['capabilities']) == len(set(tax['capabilities'])) and
            all(re.fullmatch('[a-z][a-z0-9-]{2,60}', c) for c in tax['capabilities']), 'invalid capability identities')
    for name in ('responsibilities', 'exclusions', 'queries', 'limitations'):
        strings(pack[name], 30); require(pack[name], 'domain scope, queries and limits required')
    require(isinstance(pack['aliases'], dict) and set(pack['aliases']) == set(tax['capabilities']), 'alias capability mismatch')
    require(isinstance(pack['prerequisites'], dict) and set(pack['prerequisites']) == set(tax['capabilities']), 'prerequisite capability mismatch')
    for key in tax['capabilities']:
        strings(pack['aliases'][key], 20); strings(pack['prerequisites'][key], 20)
        require(set(pack['prerequisites'][key]) <= set(tax['capabilities']) - {key}, 'invalid prerequisite')
    complete = set()
    def visit(key, seen):
        if key in complete:
            return
        require(key not in seen, 'cyclic prerequisites')
        for parent in pack['prerequisites'][key]: visit(parent, seen | {key})
        complete.add(key)
    for key in tax['capabilities']: visit(key, set())
    fields(pack['evaluation'], ['dataset', 'sha256', 'label_status'])
    text(pack['evaluation']['dataset']); require(re.fullmatch('[a-f0-9]{64}', pack['evaluation']['sha256']), 'evaluation revision required')
    require(pack['evaluation']['label_status'] == 'provisional-human-review-pending', 'unverified pack quality claim')
    return pack


def pack_for(state):
    pack = state.get('domain_pack')
    return validate_pack(pack) if 'domain_pack' in state else None


def taxonomy_for(state):
    pack = pack_for(state)
    return pack['taxonomy'] if pack else TAXONOMY


def reference(pack):
    return {'id': pack['id'], 'version': pack['version'], 'pack_sha256': digest(pack),
            'taxonomy_version': pack['taxonomy']['version']} if pack else {
            'id': 'ai-engineering', 'version': '1', 'taxonomy_version': TAXONOMY['version']}


def domain_field(pack):
    return 'domain_fit' if pack else 'ai_domain'


def check_binding(home, state):
    from tools.research_recovery import read
    path = Path(home)/'domain-binding.json'
    pack = pack_for(state)
    if pack or path.exists() or path.is_symlink():
        require(pack is not None and read(path) == reference(pack), 'domain binding missing/mismatched; do not reinterpret state as AI')


def initialize(store, name):
    from tools.research_preflight import private_state_path
    require(store.home.resolve() != private_state_path(ROOT, {}), 'default workspace is reserved for AI; select a separate private directory')
    require(name in PACKS, 'choose a reviewed built-in domain pack')
    pack = validate_pack(json.loads(PACKS[name].read_text()))
    from tools.rank_state import save_state
    from tools.research_recovery import regular
    with store.transaction() as state:
        if pack_for(state):
            require(state['domain_pack'] == pack, 'workspace pack is immutable; use a new workspace for a new revision')
            return {'domain': reference(pack), 'already_initialized': True}
        require(not state['artifacts'] and not state['withdrawn'], 'domain opt-in requires an empty private workspace')
        path = store.home/'domain-binding.json'; regular(path)
        state['domain_pack'] = deepcopy(pack)
        save_state(path, reference(pack))
    return {'domain': reference(pack), 'already_initialized': False}


def compare_workspaces(left, right, start, end):
    """Ephemeral local inspection; never persist cross-store restricted derivatives."""
    from contextlib import ExitStack
    from tools.research_evidence import timestamp
    from tools.research_coverage import coverage_payload
    require(left.home.resolve() != right.home.resolve(), 'select two different workspaces')
    begin, finish = timestamp(start), timestamp(end)
    require(begin < finish <= min(left.clock(), right.clock()), 'invalid comparison window')
    stores = sorted([left, right], key=lambda s: str(s.home.resolve()))
    with ExitStack() as stack:
        states = [stack.enter_context(s.transaction()) for s in stores]
        rows, openings = [], []
        for store, state in zip(stores, states):
            receipts = [k for k,a in state['artifacts'].items() if a['kind'] == 'receipt' and
                        begin <= timestamp(a['payload']['finished_at']) < finish]
            report, _ = coverage_payload(state, receipts, begin, finish, {})
            rows.append({'domain': reference(pack_for(state)), 'scope': report['scope'], 'counts': report['counts'],
                         'capabilities': report['capabilities'], 'segments': report['segments'],
                         'period': report['period'], 'analysis_versions': report['analysis_versions'],
                         'source_health': report['source_health'], 'receipts': report['receipts'],
                         'limitations': report['limitations']})
            openings.append({r['opening'] for r in report['openings']})
        require(rows[0]['domain'] != rows[1]['domain'], 'comparison requires different pinned domains/revisions')
        # No common taxonomy, matched source cohort or union completeness is implied.
        return {'schema_version': 1, 'status': 'descriptive-only', 'workspaces': rows,
                'conservatively_matching_opening_ids': len(openings[0] & openings[1]),
                'pooled_openings': None, 'demand_ratio': None,
                'limitations': ['Counts describe these selected windows/samples, not relative domain demand or growth.',
                   'Inspect source queries, filters, completeness, countries, languages and missing descriptions separately.',
                   'An opening can have responsibilities in both domains; unknown cross-source identities can hide overlap.',
                   'Capability labels have different meanings; no implicit crosswalk or summed employer/opening total.',
                   'Local inspection only; no stored cross-workspace report or permission to export restricted data.']}
