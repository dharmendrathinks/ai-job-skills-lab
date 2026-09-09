"""Original-language translation proposals with exact alignment and explicit review."""
import json
import re
from pathlib import Path

from tools.research_evidence import ROOT, digest, fields, require, text, strings, EvidenceError
from tools.research_analysis import qualified, _eligible
from tools.research_runtime import CodexWorker

PROMPT = ROOT / 'docs/research/prompts/translate-v1.md'
SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['segments', 'limitations'],
          'properties': {'segments': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
                         'required': ['index', 'translated'], 'properties': {'index': {'type': 'integer'}, 'translated': {'type': 'string'}}}},
                         'limitations': {'type': 'array', 'items': {'type': 'string'}}}}


def language(value):
    require(isinstance(value, str) and re.fullmatch('[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', value), 'reviewed language tag required')


def source_segments(description):
    # Keep original code-point ranges in deterministic code, not model arithmetic.
    chunks, current = [], ''
    for line in description.splitlines(keepends=True):
        if len(current) + len(line) > 1600 and current:
            chunks.append(current); current = ''
        while len(line) > 1600:
            chunks.append(line[:1600]); line = line[1600:]
        current += line
    if current: chunks.append(current)
    require(0 < len(chunks) <= 100 and ''.join(chunks) == description, 'source segmentation budget exceeded')
    return chunks


def validate_translation(output, description):
    fields(output, ['segments', 'limitations']); strings(output['limitations'])
    chunks = source_segments(description)
    require(isinstance(output['segments'], list) and len(output['segments']) == len(chunks), 'translation must cover every source segment')
    cursor, result = 0, []
    for index,(s,original) in enumerate(zip(output['segments'],chunks)):
        fields(s, ['index', 'translated']); text(s['translated'], 20000)
        require(type(s['index']) is int and s['index'] == index, 'missing, duplicate or reordered segment ID')
        result.append({**s, 'original': original, 'start': cursor, 'end': cursor + len(original)}); cursor += len(original)
    return {'segments': result, 'limitations': ['Machine translation draft; semantic fidelity and source-language assertion require human review.', *output['limitations']]}


def translate(store, observation, source_language, target_language='en', *, worker_factory=CodexWorker, refresh=False):
    language(source_language); language(target_language); require(source_language != target_language, 'source and target must differ')
    with store.transaction() as state:
        row = _eligible(state, observation); q, identity = qualified(state)
        require(row['description'], 'missing description stays untranslated')
        versions = {'schema': 'aligned-translation/1', 'segmentation': 'source-chunks/1', 'prompt': digest(PROMPT.read_text()), 'validator': digest(Path(__file__).read_text()), 'runtime': identity}
        cache = digest([observation, source_language, target_language, versions])
        existing = [k for k,a in state['artifacts'].items() if a['kind'] == 'translation-proposal' and a['payload']['cache_key'] == cache]
        if existing and not refresh: return {'proposal': existing[-1], 'cache_hit': True}
    prompt = PROMPT.read_text() + '\nUntrusted translation input JSON:\n' + json.dumps({'segments': [{'index': i, 'original': t} for i,t in enumerate(source_segments(row['description']))], 'source_language_asserted': source_language, 'target_language': target_language}, ensure_ascii=False)
    stage, output, metadata = 'runtime', None, None
    try:
        with worker_factory(store.home) as worker:
            with store.transaction() as state: _eligible(state, observation); qualified(state)
            output, metadata = worker.run(prompt, SCHEMA)
        stage = 'alignment'
        validated = validate_translation(output, row['description'])
    except (ValueError, OSError, TimeoutError):
        with store.transaction() as state:
            if observation in state['artifacts']:
                store.put(state, 'translation-failure', {'schema_version': 1, 'observation': observation, 'versions': versions,
                          'status': 'deferred', 'stage': stage, 'response': output, 'metadata': metadata,
                          'source_language': source_language, 'target_language': target_language, 'reason': 'Runtime/quota/alignment failure; original retained, no retry or paid fallback.'}, [observation])
        raise
    with store.transaction() as state:
        _eligible(state, observation); qualified(state)
        payload = {'schema_version': 1, 'observation': observation, 'source_language': source_language,
                   'target_language': target_language, 'versions': versions, 'cache_key': cache, 'metadata': metadata,
                   'status': 'pending-human-review', **validated}
        key = store.put(state, 'translation-proposal', payload, [observation, q])
    return {'proposal': key, 'cache_hit': False, 'status': 'pending-human-review'}


def review_translation(store, row):
    fields(row, ['schema_version', 'proposal', 'decision', 'reviewer', 'notes'])
    require(row['schema_version'] == 1 and row['decision'] in ('accept', 'reject'), 'invalid translation review')
    text(row['reviewer']); text(row['notes'], 4000)
    with store.transaction() as state:
        a = state['artifacts'].get(row['proposal']); require(a and a['kind'] == 'translation-proposal', 'translation unavailable')
        require(not any(x['kind'] == 'translation-review' and x['payload']['proposal'] == row['proposal'] and x['payload'] != row
                        for x in state['artifacts'].values()), 'review is immutable; revise translation instead')
        return {'review': store.put(state, 'translation-review', row, [row['proposal']]), 'decision': row['decision']}


def freeze_gold(store, row):
    from tools.research_evidence import validate_annotation
    fields(row, ['schema_version', 'language', 'split', 'annotation', 'limitations'])
    require(row['schema_version'] == 1 and row['split'] in ('held-out', 'development'), 'invalid evaluation label split')
    language(row['language']); strings(row['limitations']); require(row['limitations'], 'label limitations required')
    with store.transaction() as state:
        validate_annotation(row['annotation'], state, store.clock())
        key = store.put(state, 'language-gold', {**row, 'frozen_at': store.clock().isoformat()}, [row['annotation']['observation']])
        return {'gold': key, 'review_basis': row['annotation']['method']}


def evaluate_languages(store, pairs):
    from tools.evaluate_research import score
    from tools.research_evidence import timestamp
    require(isinstance(pairs, list) and 0 < len(pairs) <= 200, 'evaluation requires 1-200 explicit pairs')
    with store.transaction() as state:
        rows, deps = [], []
        seen = set()
        for pair in pairs:
            fields(pair, ['gold', 'analysis'])
            gold = state['artifacts'].get(pair['gold']); actual = state['artifacts'].get(pair['analysis'])
            require(gold and gold['kind'] == 'language-gold' and actual and actual['kind'] == 'analysis', 'evaluation inputs unavailable')
            g, a = gold['payload'], actual['payload']
            require(g['annotation']['observation'] == a['observation'], 'evaluation descriptions differ')
            from tools.research_coverage import analysis_version
            version = analysis_version(state, a)
            require(version is not None, 'analysis model/prompt version unavailable')
            require((g['annotation']['observation'], version) not in seen, 'duplicate example/version inflates evaluation')
            seen.add((g['annotation']['observation'], version))
            from tools.evaluate_research import atoms
            expected = {'expected_atoms': list(atoms(g['annotation'])), 'expected_class': g['annotation']['responsibility_class'], 'expected_domain': None}
            held_out = g['split'] == 'held-out' and timestamp(g['frozen_at']) <= timestamp(a['reviewed_at'])
            rows.append({**pair, 'language': g['language'], 'analysis_version': version, 'analysis_method': a['method'],
                         'label_basis': g['annotation']['method'], 'held_out_by_recorded_order': held_out, **score({**a, 'ai_domain': a.get('ai_domain')}, expected)})
            deps += [pair['gold'], pair['analysis']]
        groups = {}
        for row in rows:
            label = row['language'] + ':' + row['analysis_version']
            group = groups.setdefault(label, {'examples': 0, 'true_positive': 0, 'false_positive': 0, 'false_negative': 0,
                                               'class_correct': 0, 'held_out_examples': 0})
            group['examples'] += 1; group['held_out_examples'] += row['held_out_by_recorded_order']
            for n in ('true_positive', 'false_positive', 'false_negative', 'class_correct'): group[n] += row[n] or 0
        for group in groups.values():
            tp,fp,fn = (group[n] for n in ('true_positive', 'false_positive', 'false_negative'))
            group['precision'] = tp/(tp+fp) if tp+fp else None
            group['recall'] = tp/(tp+fn) if tp+fn else None
        result = {'schema_version': 1, 'examples': rows, 'by_language_version': groups,
                  'targets_not_results': {'precision': .95, 'recall': .85}, 'promotion': 'requires_human_review_no_automatic_language_promotion',
                  'limitations': ['Record order does not prove the model never saw a held-out example.',
                                  'Human/synthetic labels and analysis methods are disclosed; test fixtures do not establish model quality.',
                                  'Translation fidelity must be reviewed separately; extraction metrics do not score translation.']}
        key = store.put(state, 'language-evaluation', result, deps)
        return {'evaluation': key, 'by_language_version': groups, 'promotion': result['promotion']}
