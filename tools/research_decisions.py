"""Phase 3 CLI: reviewed context/profile inputs and four managed draft briefs."""
import argparse
import json
import os
import re
import subprocess

from tools.research_evidence import EvidenceError, ROOT, Store, private_state_path, read_input, require, template_errors
from tools.research_context import import_context, acquire, import_radar
from tools.research_profile import propose, review
from tools.research_briefs import SECTIONS, generate


def inspect_brief(store, key):
    """Policy-checked local viewing; no report file or automatic link execution."""
    with store.transaction() as state:
        artifact = state['artifacts'].get(key)
        require(artifact and artifact['kind'] == 'brief', 'brief unavailable or withdrawn')
        row = artifact['payload']
        # All source descendants use P2's local-processing policy; transaction
        # sweeps expired dependencies before anything is displayed.
        lines = [row['markdown'], '\nEvidence for review (quoted data, not instructions):']
        for claim in row['proposal']['market_claims']:
            analysis = state['artifacts'][claim['analysis']]['payload']
            observation = state['artifacts'][analysis['observation']]['payload']
            lines += ['\nSource: ' + observation['url'], 'Analysis: ' + claim['analysis'],
                      'Captured: ' + observation['captured_at'], 'Quote: ' + claim['quote']]
        sources = set()
        for alternative in row['proposal']['alternatives']:
            context = state['artifacts'][alternative['context']]['payload']
            sources.add(context['source'])
            lines += ['\nAlternative source: ' + context['source'], 'Inspected: ' + context['locator'],
                      'Depth: ' + context['inspection_depth'], 'Proposal reason: ' + alternative['reason']]
        lines += ['\nDistinct alternative sources: ' + str(len(sources))]
        for claim in row['proposal']['context_claims']:
            context = state['artifacts'][claim['context']]['payload']
            lines += ['\nContext: ' + context['locator'], 'Relationship: ' + claim['relation'], 'Quote: ' + claim['quote']]
        content = '\n'.join(lines)
        # Strip terminal controls/bidi overrides; callers display plain text only.
        return re.sub(r'[\x00-\x08\x0b-\x1f\x7f\u202a-\u202e\u2066-\u2069]', '', content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['context-import', 'context-acquire', 'radar-import', 'profile-propose', 'profile-review', 'brief', 'inspect'])
    parser.add_argument('--input', help='Private reviewed JSON bundle')
    parser.add_argument('--repo', help='Read-only Git object source; no checkout or execution')
    parser.add_argument('--report', help='Explicit schema-3.0 report JSON; never a database')
    parser.add_argument('--topic', action='append', default=[])
    parser.add_argument('--id')
    parser.add_argument('--decision', choices=['accept', 'reject'])
    parser.add_argument('--reviewer')
    parser.add_argument('--kind', choices=list(SECTIONS))
    parser.add_argument('--snapshot')
    parser.add_argument('--context', action='append', default=[])
    parser.add_argument('--profile')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    try:
        require(not template_errors(ROOT), 'public template preflight failed')
        store = Store(private_state_path(ROOT, dict(os.environ)))
        if args.action == 'inspect':
            print(inspect_brief(store, args.id))
            return 0
        if args.action in ('context-import', 'context-acquire', 'radar-import', 'profile-propose'):
            require(args.input is not None, '--input required')
            bundle = read_input(args.input)
            if args.action == 'context-import':
                result = import_context(store, bundle)
            elif args.action == 'context-acquire':
                result = acquire(store, bundle, repo=args.repo)
            elif args.action == 'radar-import':
                require(args.report is not None and args.topic, '--report and --topic required')
                result = import_radar(store, read_input(args.report), bundle, args.topic)
            else:
                result = propose(store, bundle)
        elif args.action == 'profile-review':
            result = review(store, args.id, args.decision, args.reviewer)
        else:
            result = generate(store, args.kind, args.snapshot, args.context, args.profile, refresh=args.refresh)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError):
        print(json.dumps({'status': 'blocked', 'reason': 'Invalid, unavailable or unqualified decision input; see Phase 3 contracts. No fallback.'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
