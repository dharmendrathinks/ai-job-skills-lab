"""Domain pack inspection, explicit workspace opt-in and bounded comparisons."""
import argparse
import json
import os
from tools.research_evidence import ROOT, Store, private_state_path, require, template_errors
from tools.research_domains import PACKS, initialize, pack_for, reference, compare_workspaces


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['packs', 'init', 'status', 'compare', 'evaluate'])
    p.add_argument('--pack', choices=list(PACKS)); p.add_argument('--other-home')
    p.add_argument('--from', dest='start'); p.add_argument('--to', dest='end')
    args = p.parse_args()
    try:
        require(not template_errors(ROOT), 'public template check failed')
        store = Store(private_state_path(ROOT, dict(os.environ)))
        if args.action == 'packs':
            result = {'default': 'ai-engineering', 'opt_in': {k:json.loads(v.read_text()) for k,v in PACKS.items()}}
        elif args.action == 'init':
            require(os.environ.get('AI_JOB_RADAR_HOME'), 'explicit private AI_JOB_RADAR_HOME required for opt-in')
            result = initialize(store, args.pack)
        elif args.action == 'status':
            with store.transaction() as state: result = {'domain': reference(pack_for(state))}
        elif args.action == 'compare':
            require(args.other_home, 'explicit other workspace required')
            other = Store(private_state_path(ROOT, {'AI_JOB_RADAR_HOME': args.other_home}))
            result = compare_workspaces(store, other, args.start, args.end)
        else:
            from tools.evaluate_domains import evaluate
            result = evaluate(store)
        print(json.dumps(result, sort_keys=True)); return 0
    except (ValueError, OSError, TypeError, KeyError):
        print(json.dumps({'status': 'blocked', 'action': args.action,
              'detail': 'Check workspace binding, source policy, domain revision and runtime qualification.'})); return 1


if __name__ == '__main__':
    raise SystemExit(main())
