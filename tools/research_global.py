"""Phase 5 registry, coverage, cohort, original-language and board review commands."""
import argparse
import json
import os
import re

from tools.research_evidence import ROOT, Store, private_state_path, template_errors, require, read_input, fields
from tools.research_coverage import (coverage, register_protocol, assess_capture, review_segments, register_board,
                                     link_board, define_cohort, compare, vacancy_view)
from tools.research_languages import translate, review_translation, freeze_gold, evaluate_languages

REGISTRY = ROOT / 'docs/research/source-registry-v1.json'
PACKS = ROOT / 'docs/research/query-packs-v1.json'
SOURCES = {'greenhouse', 'lever', 'ashby', 'smartrecruiters', 'himalayas', 'jobicy', 'linkedin', 'indeed',
           'glassdoor', 'google-jobs', 'ziprecruiter', 'freehire', 'jobbank', 'jobdanmark', 'jobindex', 'jobnet'}


def registry():
    row = read_input(REGISTRY)
    fields(row, ['schema_version', 'revision', 'review_date', 'sources'])
    require(row['schema_version'] == 1 and {r['id'] for r in row['sources']} == SOURCES
            and len(row['sources']) == len(SOURCES), 'invalid source registry inventory')
    for r in row['sources']:
        fields(r, ['id', 'disposition', 'implementation', 'mechanism', 'authentication_and_cost', 'coverage_and_completeness',
                   'reference', 'inspection_evidence', 'gap_and_gate', 'validation_steps', 'limitations', 'phase'])
        require(r['disposition'] in ('go-limited', 'conditional', 'no-go'), 'invalid source disposition')
        require(r['disposition'] != 'go-limited' or r['id'] == 'jobicy', 'new source promotion requires implemented qualified collector')
    return row


def display_json(value):
    # Keep Hindi/other source languages readable while terminal controls remain
    # JSON-escaped and bidirectional overrides cannot reorder the review UI.
    rendered = json.dumps(value, ensure_ascii=False, indent=2)
    return re.sub(r'[\u202a-\u202e\u2066-\u2069]', lambda m: '\\u%04x' % ord(m.group()), rendered)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['registry', 'query-pack', 'ai-query-plan', 'coverage', 'protocol', 'capture-assess', 'segments', 'board',
                                         'board-link', 'cohort', 'compare', 'vacancies', 'translate', 'translation-review',
                                         'language-gold', 'language-evaluate', 'inspect'])
    parser.add_argument('--input'); parser.add_argument('--id'); parser.add_argument('--from', dest='start')
    parser.add_argument('--to', dest='end'); parser.add_argument('--language'); parser.add_argument('--target', default='en')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    try:
        require(not template_errors(ROOT), 'public template preflight failed')
        if args.action == 'registry': result = registry()
        elif args.action == 'query-pack':
            packs = read_input(PACKS)
            result = {**packs, 'packs': [p for p in packs['packs'] if not args.language or p['language'] == args.language]}
            require(result['packs'], 'query language not available')
        else:
            store = Store(private_state_path(ROOT, dict(os.environ)))
            if args.action == 'ai-query-plan':
                from tools.research_sources import ai_query_plan
                with store.transaction() as state:
                    require('domain_pack' not in state, 'AI query plan belongs to the default AI domain')
                    result = ai_query_plan(state, store.clock())
            elif args.action == 'coverage': result = coverage(store, start=args.start, end=args.end, expected=read_input(args.input) if args.input else None)
            elif args.action == 'compare': result = compare(store, args.id)
            elif args.action == 'vacancies': result = vacancy_view(store, args.id)
            elif args.action == 'translate': result = translate(store, args.id, args.language, args.target, refresh=args.refresh)
            elif args.action == 'inspect':
                with store.transaction() as state:
                    a = state['artifacts'].get(args.id)
                    require(a and a['kind'] in ('coverage-report', 'cohort-comparison', 'vacancy-view', 'translation-proposal',
                                               'translation-review', 'language-evaluation', 'employer-board', 'collection-protocol'), 'view unavailable')
                    result = {'kind': a['kind'], 'payload': a['payload']}
            else:
                require(args.input, 'reviewed input required')
                fn = {'protocol': register_protocol, 'capture-assess': assess_capture, 'segments': review_segments,
                      'board': register_board, 'board-link': link_board, 'cohort': define_cohort, 'translation-review': review_translation,
                      'language-gold': freeze_gold, 'language-evaluate': evaluate_languages}[args.action]
                result = fn(store, read_input(args.input))
        print(display_json(result))
        return 0
    except (ValueError, TypeError, KeyError, OSError):
        print(json.dumps({'status': 'blocked', 'reason': 'Invalid, unavailable or unqualified global-research input; see coverage contracts. No fallback.'}))
        return 1


if __name__ == '__main__': raise SystemExit(main())
