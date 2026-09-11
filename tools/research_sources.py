"""One qualified conditional source, using the shared research state contracts.

Freehire stays the preferred upstream collector pending its research-data review.
Jobicy fills that demonstrated permission gap; no other portal is replaced.
"""
from datetime import timedelta
from html import unescape
from html.parser import HTMLParser
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from tools.research_evidence import EvidenceError, digest, require, timestamp, validate_policy

POLICY_REFERENCE = "https://github.com/Jobicy/remote-jobs-api/blob/c38dc5308768d7a9c0228c4831b453530f4788d9/README.md#fair-use"
ENDPOINT = "https://jobicy.com/api/v2/remote-jobs"


AI_QUERY_REVISION = 'ai-engineering-queries/1'
# Discovery seeds, not evidence of a responsibility or guarantee of role coverage.
AI_QUERIES = (
    ('LLM applications and tools', 'LLM'),
    ('AI product engineering', 'AI product'),
    ('Applied AI engineering', 'applied AI'),
    ('General AI engineering', 'AI engineer'),
    ('Generative AI applications', 'generative AI'),
    ('Agents and automation', 'AI agent'),
    ('Retrieval and knowledge systems', 'retrieval'),
    ('Evaluation and reliability', 'LLM evaluation'),
    ('AI security', 'AI security'),
    ('Inference and deployment', 'inference'),
    ('AI infrastructure and platforms', 'AI infrastructure'),
    ('ML operations and pipelines', 'MLOps'),
    ('Relevant ML engineering and research', 'machine learning'),
)


def ai_query_plan(state, now):
    attempts = [a['payload'] for a in state['artifacts'].values()
                if a['kind'] == 'collection-attempt' and a['payload']['source'] == 'jobicy']
    receipts = [a['payload'] for a in state['artifacts'].values()
                if a['kind'] == 'receipt' and a['payload']['source'] == 'jobicy']
    rows = []
    for area, query in AI_QUERIES:
        runs = [a for a in attempts if a['query'] == query]
        captures = [r for r in receipts if r['query'] == query]
        rows.append({'area': area, 'query': query, 'attempts': len(runs),
                     'last_attempt': max((a['attempted_at'] for a in runs), default=None),
                     'successful_requests': sum(r['completeness'] != 'failed' for r in captures),
                     'returned_observations': sum(p['returned'] for r in captures for p in r['pages']),
                     'status': 'pending' if not runs else 'attempted-not-proof-of-role-coverage'})
    selected = min(enumerate(rows), key=lambda pair: (
        timestamp(pair[1]['last_attempt']) if pair[1]['last_attempt'] else timestamp('1970-01-01T00:00:00Z'), pair[0]))[1]
    latest = max((timestamp(a['attempted_at']) for a in attempts), default=None)
    available = latest + timedelta(hours=1) if latest else now
    return {'revision': AI_QUERY_REVISION, 'source': 'jobicy', 'queries': rows,
            'next_query': selected['query'], 'next_area': selected['area'],
            'manual_ready': True, 'scheduled_eligible_at': max(now, available).isoformat(),
            'scheduled_ready': now >= available,
            'limitations': ['Discovery seeds are not validated requirements, role labels or measured recall.',
                           'One query per explicitly invoked collection; no automatic schedule or polling loop.',
                           'Single remote-biased source; capped/failed/empty results do not establish role absence.',
                           'Attempt counts and returned revisions are not distinct openings or demand growth.']}


class PlainHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag in ("p", "li", "div", "br", "h1", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.hidden:
            self.hidden -= 1
        if tag in ("p", "li", "div", "h1", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def html_text(value):
    parser = PlainHTML()
    parser.feed(value)
    return "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())


def jobicy_policy():
    return {
        "schema_version": 1, "source": "jobicy", "method": "jobicy-api-v2",
        "reviewed_by": "Codex source-document inspection; not legal counsel or human sign-off",
        "reviewed_at": "2026-09-09T00:00:00Z", "use_until": "2026-10-09T00:00:00Z",
        "permission_basis": "Documented API permits research/AI products, summaries and appropriate caching with attribution; no hard deletion deadline is stated for this narrow use.",
        "permission_reference": POLICY_REFERENCE, "local_processing": True,
        "retention": "indefinite-logical-deletion", "hosted_disclosure": True,
        "hosted_retention": "provider-managed-no-deletion-deadline",
        "hosted_permission_reference": POLICY_REFERENCE,
        "export": False, "audit_hashes": True,
        "limitations": ["Review expires after 30 days; access expiry is not guaranteed physical erasure.",
                        "API terms do not transfer employer-content ownership; no bulk republication or model training.",
                        "Keep source attribution/canonical URL; hosted copies cannot be recalled by this tool.",
                        "Remote-biased sample; no complete worldwide coverage or current-vacancy guarantee."],
    }


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise EvidenceError("source redirect requires review")


def fetch_jobicy(query, count):
    url = ENDPOINT + "?" + urlencode({"count": count, "tag": query})
    request = Request(url, headers={"User-Agent": "AI-Job-Skills-Lab/0.2 (bounded research; no automated retries)",
                                   "Accept": "application/json"})
    with build_opener(NoRedirect).open(request, timeout=25) as response:
        body = response.read(2_000_001)
        require(len(body) <= 2_000_000, "source response exceeds capture budget")
        require("json" in response.headers.get("Content-Type", ""), "source did not return JSON")
        return json.loads(body), url


def collect_jobicy(store, query=None, count=100, *, scheduled=False, fetch=fetch_jobicy):
    require(type(scheduled) is bool, "scheduled must be a boolean")
    require(query is None or isinstance(query, str) and 3 <= len(query) <= 50, "query must be 3–50 characters")
    require(type(count) is int and 1 <= count <= 100, "capture count must be 1–100")
    now = store.clock()
    policy = jobicy_policy()
    validate_policy(policy, now)  # before any request or persistence
    with store.transaction() as state:
        rotation = query is None
        if rotation:
            query = ai_query_plan(state, now)["next_query"]
        previous = [a["payload"]["attempted_at"] for a in state["artifacts"].values()
                    if a["kind"] == "collection-attempt" and a["payload"]["source"] == "jobicy"]
        require(not scheduled or not previous or now - max(map(timestamp, previous)) >= timedelta(hours=1),
                "Scheduled Jobicy polling must wait at least one hour after the last attempt")
        policy_id = store.put(state, "policy", policy, use_until=policy["use_until"])
        attempt = store.put(state, "collection-attempt", {"source": "jobicy", "attempted_at": now.isoformat(),
                            "query": query, "count": count, "trigger": "scheduled" if scheduled else "manual",
                            **({"query_pack_revision": AI_QUERY_REVISION} if rotation else {})}, [policy_id])
    receipt = {"schema_version": 1, "source": "jobicy", "kind": "job", "query": query,
               "requested_filters": {"count": count, "tag": query},
               "effective_filters": {"count": count, "tag": query},
               "started_at": now.isoformat(), "finished_at": now.isoformat(), "pages": [],
               "completeness": "partial", "limitations": ["Single capped feed; no total or pagination proof.",
                   "Remote source bias is not a research eligibility filter. Countries/languages may be unknown."]}
    if rotation:
        receipt["limitations"].append("Discovery query pack: " + AI_QUERY_REVISION + "; keyword matches are not role classification.")
    try:
        raw, url = fetch(query, count)
        jobs = raw.get("jobs")
        require(isinstance(jobs, list) and len(jobs) <= count, "unexpected source envelope or count")
        captured = store.clock().isoformat()
        observations = []
        for job in jobs:
            require(isinstance(job, dict) and type(job.get("id")) is int, "source job ID missing")
            canonical = job.get("url", "")
            parsed = urlparse(canonical)
            require(parsed.scheme == "https" and parsed.hostname == "jobicy.com" and parsed.path.startswith("/jobs/"),
                    "source canonical URL outside reviewed host")
            html = job.get("jobDescription")
            description = html_text(html) if isinstance(html, str) and html.strip() else None
            row = {"native_id": str(job["id"]), "employer_name": job.get("companyName"),
                   "employer_domain": None, "employer_requisition": None, "url": canonical,
                   "title": unescape(job.get("jobTitle", "")), "description": description,
                   "captured_at": captured, "source_revision": digest(job),
                   "posted_at_original": job.get("pubDate"), "posted_at": None,
                   "language": None, "country": None, "availability": "unknown",
                   "availability_evidence": None,
                   "segments": {"source_geography": job.get("jobGeo"), "arrangement": "remote",
                                "seniority": job.get("jobLevel"), "employment_type": job.get("jobType")},
                   "limitations": ["Feed inclusion is not independent availability verification.",
                                    "Employer domain/requisition and description language not verified."]}
            if description:
                row.update(raw_description=html, description_transform="html-text/1")
            if row["posted_at_original"]:
                try:
                    row["posted_at"] = timestamp(row["posted_at_original"]).isoformat()
                except EvidenceError:
                    row["limitations"].append("Publication timezone unknown; original value preserved.")
            observations.append(row)
        receipt.update(finished_at=captured, pages=[{"locator": url, "status": "ok", "returned": len(jobs),
                                                     "next_cursor": None}])
        result = store.import_bundle({"schema_version": 1, "policy": policy, "receipt": receipt,
                                      "observations": observations})
        # Do not store unused salary/logo fields or the transport response as an extra copy.
        return {**result, "attempt": attempt}
    except (EvidenceError, HTTPError, URLError, ValueError, TypeError, OSError):
        receipt.update(finished_at=store.clock().isoformat(), completeness="failed",
                       pages=[{"locator": ENDPOINT, "status": "failed", "returned": 0, "next_cursor": None}])
        store.import_bundle({"schema_version": 1, "policy": policy, "receipt": receipt, "observations": []})
        raise EvidenceError("Jobicy acquisition failed; attempt recorded, no fallback or automatic retry") from None
