"""Research decisions: context, briefs, reviewed outcomes and interchange."""
import argparse
import json
import os
import re
import subprocess

from tools.research_evidence import EvidenceError, ROOT, Store, private_state_path, read_input, require, template_errors
from tools.research_context import import_context, acquire, import_radar
from tools.research_profile import propose, review
from tools.research_briefs import SECTIONS, generate
from tools.research_outcomes import decide, record_outcome, reconsider, propose_from_outcome, history
from tools.research_interchange import preview, release, import_interchange


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
    parser.add_argument('action', choices=['context-import', 'context-acquire', 'radar-import', 'profile-propose', 'profile-review', 'brief', 'inspect', 'decide', 'outcome', 'reconsider', 'history', 'outcome-profile', 'interchange-preview', 'interchange-release', 'interchange-import', 'interchange-inspect', 'skills', 'skill-history', 'skill-map', 'path-propose', 'path-compare', 'path-select', 'path-decision', 'path-briefs', 'progress', 'progress-profile', 'ask', 'learning-inspect', 'curricula', 'curriculum-inspect'])
    parser.add_argument('--input', help='Private reviewed JSON bundle')
    parser.add_argument('--repo', help='Read-only Git object source; no checkout or execution')
    parser.add_argument('--report', help='Explicit schema-3.0 report JSON; never a database')
    parser.add_argument('--topic', action='append', default=[])
    parser.add_argument('--id')
    parser.add_argument('--decision', choices=['accept', 'reject'])
    parser.add_argument('--reviewer')
    parser.add_argument('--kind', choices=list(SECTIONS))
    parser.add_argument('--snapshot')
    parser.add_argument('--curriculum', help='Versioned curated AI learning path')
    parser.add_argument('--preferences', help='Private JSON planning preferences; never application profile data')
    parser.add_argument('--cohort', help='Reviewed equal-window cohort for skill trends')
    parser.add_argument('--context', action='append', default=[])
    parser.add_argument('--profile')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--reconsideration')
    parser.add_argument('--exchange', action='append', default=[])
    parser.add_argument('--review-digest')
    parser.add_argument('--direction', action='append', default=[])
    parser.add_argument('--skill', action='append', default=[])
    parser.add_argument('--days', type=int, default=30)
    parser.add_argument('--basis', choices=['capture', 'publication'], default='capture')
    parser.add_argument('--source'); parser.add_argument('--responsibility')
    parser.add_argument('--question'); parser.add_argument('--intent', choices=['auto', 'count', 'explain', 'recommend'], default='auto')
    parser.add_argument('--retry-review', help='Explicit operator reason for retrying a failed/ambiguous learning intent')
    args = parser.parse_args()
    try:
        require(not template_errors(ROOT), 'public template preflight failed')
        if args.action in ('curricula', 'curriculum-inspect'):
            from tools.research_curricula import inspect_curriculum
            if args.action == 'curriculum-inspect': require(args.curriculum or args.id, '--curriculum required')
            print(json.dumps(inspect_curriculum(args.curriculum or args.id if args.action == 'curriculum-inspect' else None), ensure_ascii=True, indent=2))
            return 0
        store = Store(private_state_path(ROOT, dict(os.environ)))
        if args.action in ('skills', 'skill-history', 'skill-map', 'path-propose', 'path-compare', 'path-select', 'path-decision', 'path-briefs', 'progress', 'progress-profile', 'ask', 'learning-inspect'):
            from tools.research_skills import snapshot as skill_snapshot, monthly, review_mapping
            from tools.research_learning import propose_path, select_path, record_progress, progress_profile, path_decision, compare_path
            if args.action == 'skills': result = skill_snapshot(store, days=args.days, basis=args.basis, source=args.source, responsibility=args.responsibility)
            elif args.action == 'skill-history': result = monthly(store, args.days, basis=args.basis, cohort=args.cohort)
            elif args.action == 'skill-map': result = review_mapping(store, read_input(args.input))
            elif args.action == 'path-propose':
                if args.curriculum:
                    from tools.research_curricula import propose_curriculum
                    result = propose_curriculum(store, args.curriculum, args.snapshot, read_input(args.preferences) if args.preferences else None, contexts=args.context, retry_review=args.retry_review)
                else:
                    require(not args.preferences, '--preferences currently requires --curriculum')
                    result = propose_path(store, args.snapshot, args.skill, args.context, args.profile, retry_review=args.retry_review)
            elif args.action == 'path-compare': result = compare_path(store, args.id, retry_review=args.retry_review)
            elif args.action == 'path-select': result = select_path(store, args.id, args.reviewer)
            elif args.action == 'path-decision': result = path_decision(store, read_input(args.input))
            elif args.action == 'progress': result = record_progress(store, read_input(args.input))
            elif args.action == 'progress-profile': result = progress_profile(store, args.id)
            elif args.action == 'path-briefs':
                from tools.research_learning import path_briefs
                result = path_briefs(store, args.id, retry_review=args.retry_review, refresh=args.refresh)
            elif args.action == 'ask':
                from tools.research_questions import answer
                require(len(args.skill) <= 1, 'ask accepts one skill filter')
                result = answer(store, args.snapshot, args.question, args.intent, args.skill[0] if args.skill else None, retry_review=args.retry_review)
            else:
                from tools.research_outcomes import artifact
                with store.transaction() as state:
                    result = artifact(state, args.id, ('skill-snapshot', 'skill-history', 'skill-mapping', 'learning-path', 'learning-selection', 'learning-progress', 'learning-decision', 'learning-comparison', 'evidence-answer'))
            print(json.dumps(result, ensure_ascii=True, indent=2)); return 0
        if args.action == 'interchange-inspect':
            from tools.research_outcomes import artifact
            with store.transaction() as state:
                row = artifact(state, args.id, ('interchange-item',))
                print(json.dumps({'status': 'imported-assessment-only', 'item': row}, ensure_ascii=True, indent=2))
            return 0
        if args.action == 'history':
            # Local view uses the same terminal-control filtering as brief inspection.
            print(re.sub(r'[\x00-\x1f\x7f\u202a-\u202e\u2066-\u2069]', '', json.dumps(history(store, args.id), ensure_ascii=True)))
            return 0
        if args.action == 'inspect':
            print(inspect_brief(store, args.id))
            return 0
        if args.action in ('decide', 'outcome', 'reconsider', 'interchange-preview', 'interchange-import'):
            require(args.input is not None, '--input required')
            data = read_input(args.input)
            if args.action == 'decide': result = decide(store, data)
            elif args.action == 'outcome': result = record_outcome(store, data)
            elif args.action == 'reconsider': result = reconsider(store, data)
            elif args.action == 'interchange-preview': result = preview(store, data)
            else:
                from tools.research_evidence import fields
                fields(data, ['bundle', 'policy'])
                result = import_interchange(store, data['bundle'], data['policy'])
        elif args.action == 'outcome-profile':
            result = propose_from_outcome(store, args.id, args.direction, args.profile)
        elif args.action == 'interchange-release':
            result = release(store, args.id, args.review_digest, args.reviewer)
        elif args.action in ('context-import', 'context-acquire', 'radar-import', 'profile-propose'):
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
            result = generate(store, args.kind, args.snapshot, args.context, args.profile, refresh=args.refresh, reconsideration=args.reconsideration, exchanges=args.exchange)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError):
        print(json.dumps({'status': 'blocked', 'reason': 'Invalid, unavailable or unqualified decision input; see decision/outcome contracts. No fallback.'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
