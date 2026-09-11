"""Optional reviewed Slack delivery; no sends during refresh or scheduled ticks.

Selective design reuse: pinned Radar slack.py destination identity, bounded
presentation, no link unfurls, independent delivery ledger. No code imported.
"""
import json
import re
from urllib.request import build_opener, ProxyHandler, HTTPRedirectHandler, Request

from tools.research_evidence import digest, require, text
from tools.research_operations import run_lock, ledger, save_ledger, inbox_rows
from tools.research_outcomes import artifact
from tools.research_interchange import exportable


def destination(value):
    require(isinstance(value, str) and re.fullmatch(
        r'https://hooks\.slack\.com/services/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+', value),
        'destination must be an explicit Slack incoming webhook; redirects/proxies disabled')
    return digest(value)


def preview_notification(store, webhook, limit=10):
    target = destination(webhook)
    require(type(limit) is int and 1 <= limit <= 10, 'notification limit must be 1–10')
    with run_lock(store):
        log = ledger(store)
        delivered = {i for r in log['deliveries'].values() if r['destination'] == target for i in r['items']}
        with store.transaction() as state:
            rows = [r for r in inbox_rows(state, store.clock()) if r['status'] != 'deferred' and r['identity'] not in delivered]
            selected = rows[:limit]
            require(selected, 'no undelivered changes; uncertain deliveries require manual reconciliation')
            exportable(state, [r['brief'] for r in selected], store.clock())
            # No generated prose, private profile, title, URL, tracking or automatic link unfurl.
            payload = {'text': 'AI Job Skills Lab: ' + str(len(selected)) + ' research drafts ready for local review.\n' +
                       '\n'.join(r['kind'] + ' revision ' + str(r['revision']) + ': ' + r['brief'] for r in selected),
                       'unfurl_links': False, 'unfurl_media': False}
            row = {'schema_version': 1, 'destination': target, 'items': [r['identity'] for r in selected],
                   'payload': payload, 'overflow': len(rows)-len(selected)}
            key = store.put(state, 'notification-preview', row,
                            [r['brief'] for r in selected] + [r['decision'] for r in selected if r['decision']])
            return {'preview': key, 'review_digest': digest(row), **row}


def approve_notification(store, key, review_digest, webhook, reviewer):
    text(reviewer)
    with store.transaction() as state:
        row = artifact(state, key, ('notification-preview',))
        exportable(state, [key], store.clock())
        require(digest(row) == review_digest and destination(webhook) == row['destination'],
                'approval must match exact content and destination')
        return {'approval': store.put(state, 'notification-approval', {'preview': key,
                'review_digest': review_digest, 'destination': row['destination'], 'reviewer': reviewer,
                'approved_at': store.clock().isoformat()}, [key])}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def post(webhook, payload):
    request = Request(webhook, json.dumps(payload).encode(), {'Content-Type': 'application/json'}, method='POST')
    with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=10) as response:
        require(response.status == 200 and response.read(16).strip() == b'ok', 'unconfirmed delivery')


def send_notification(store, approval, webhook, *, transport=post):
    target = destination(webhook)
    with run_lock(store):
        log = ledger(store)
        with store.transaction() as state:
            permit = artifact(state, approval, ('notification-approval',))
            row = artifact(state, permit['preview'], ('notification-preview',))
            exportable(state, [approval], store.clock())
            require(target == permit['destination'] == row['destination'] and digest(row) == permit['review_digest'],
                    'destination or reviewed content changed')
            key = digest([target, row['items']])
            previous = [r for r in log['deliveries'].values() if r['destination'] == target and set(r['items']) & set(row['items'])]
            require(not previous, 'already sent or ambiguous; no automatic retry')
            log['deliveries'][key] = {'destination': target, 'items': row['items'], 'status': 'ambiguous',
                                       'attempted_at': store.clock().isoformat()}
            save_ledger(store, log)  # record intent before possible external write
            try:
                transport(webhook, row['payload'])
            except Exception:
                # Exception details can include webhook credentials. Never persist or echo them.
                raise ValueError('delivery unconfirmed; inspect destination manually; automatic retry blocked') from None
            log['deliveries'][key]['status'] = 'sent'
            save_ledger(store, log)
            return {'delivery': key, 'status': 'sent'}
