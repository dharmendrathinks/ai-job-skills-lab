"""Local operational entry point. Every external delivery needs its own approval."""
import argparse
import json
import os
import subprocess

from tools.research_evidence import Store, ROOT, private_state_path, read_input, template_errors, require
from tools.research_operations import configure, execute, inbox, report, tick, health, launchd, resolve_step
from tools.research_recovery import backup, restore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['configure', 'run', 'tick', 'inbox', 'report', 'cleanup', 'health',
                                         'backup', 'restore', 'launchd', 'notify-preview', 'notify-approve', 'notify-send', 'resolve'])
    parser.add_argument('--input')
    parser.add_argument('--plan')
    parser.add_argument('--resume')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--acknowledge', action='store_true')
    args = parser.parse_args()
    try:
        require(not template_errors(ROOT), 'public template preflight failed')
        store = Store(private_state_path(ROOT, dict(os.environ)))
        if args.action in ('report', 'run', 'tick'):
            from tools.research_report_files import bind
            bind(store, ROOT)
        if args.action == 'configure': result = configure(store, read_input(args.input))
        elif args.action == 'run': result = execute(store, args.plan, resume=args.resume)
        elif args.action == 'tick': result = tick(store, args.plan)
        elif args.action == 'inbox': result = inbox(store, args.limit, acknowledge=args.acknowledge)
        elif args.action == 'report': result = report(store, args.limit)
        elif args.action == 'cleanup': result = health(store)
        elif args.action == 'health': result = health(store)
        elif args.action == 'backup': result = backup(store)
        elif args.action == 'restore': result = restore(store)
        elif args.action == 'resolve':
            row = read_input(args.input)
            result = resolve_step(store, row['run'], row['step'], row['action'], row['reviewer'], row['reason'])
        elif args.action == 'launchd':
            print(launchd(store, args.plan)); return 0
        else:
            from tools.research_delivery import preview_notification, approve_notification, send_notification
            row = read_input(args.input)  # webhook never passed on process command line
            if args.action == 'notify-preview': result = preview_notification(store, row['webhook'], min(args.limit, 10))
            elif args.action == 'notify-approve': result = approve_notification(store, row['preview'], row['review_digest'], row['webhook'], row['reviewer'])
            else: result = send_notification(store, row['approval'], row['webhook'])
        print(json.dumps(result, sort_keys=True))
        return 1 if result.get('status') in ('failed', 'needs-review') else 0
    except (ValueError, OSError, TypeError, KeyError, subprocess.SubprocessError):
        # Notification URLs or imported text must not enter launchd/log/terminal errors.
        print(json.dumps({'status': 'blocked', 'action': args.action, 'detail': 'Check private inputs, lifecycle, qualification and operations health.'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
