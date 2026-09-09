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
    request = Request(url, headers={"User-Agent": "AI-Job-Radar/0.2 (bounded research; no automated retries)",
                                   "Accept": "application/json"})
    with build_opener(NoRedirect).open(request, timeout=25) as response:
        body = response.read(2_000_001)
        require(len(body) <= 2_000_000, "source response exceeds capture budget")
        require("json" in response.headers.get("Content-Type", ""), "source did not return JSON")
        return json.loads(body), url


def collect_jobicy(store, query="machine learning", count=20, *, fetch=fetch_jobicy):
    require(isinstance(query, str) and 3 <= len(query) <= 50, "query must be 3–50 characters")
    require(type(count) is int and 1 <= count <= 100, "capture count must be 1–100")
    now = store.clock()
    policy = jobicy_policy()
    validate_policy(policy, now)  # before any request or persistence
    with store.transaction() as state:
        previous = [a["payload"]["attempted_at"] for a in state["artifacts"].values()
                    if a["kind"] == "collection-attempt" and a["payload"]["source"] == "jobicy"]
        require(not previous or now - max(map(timestamp, previous)) >= timedelta(hours=1),
                "Jobicy polling cooldown: wait at least one hour, including after failures")
        policy_id = store.put(state, "policy", policy, use_until=policy["use_until"])
        attempt = store.put(state, "collection-attempt", {"source": "jobicy", "attempted_at": now.isoformat(),
                            "query": query, "count": count}, [policy_id])
    receipt = {"schema_version": 1, "source": "jobicy", "kind": "job", "query": query,
               "requested_filters": {"count": count, "tag": query},
               "effective_filters": {"count": count, "tag": query},
               "started_at": now.isoformat(), "finished_at": now.isoformat(), "pages": [],
               "completeness": "partial", "limitations": ["Single capped feed; no total or pagination proof.",
                   "Remote source bias is not a research eligibility filter. Countries/languages may be unknown."]}
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
