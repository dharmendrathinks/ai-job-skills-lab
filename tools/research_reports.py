"""Offline presentation only. Untrusted text never becomes markup or script."""
import base64
import hashlib
from html import escape
import json
import re

from tools.research_evidence import aggregate
from tools.research_outcomes import latest_decisions
from tools.research_report_roles import role_families, VERSION as ROLE_VERSION, OTHER

from pathlib import Path

ASSETS = Path(__file__).with_name('report_assets')
SCRIPT = (ASSETS / 'workspace.js').read_text()

STYLE = (ASSETS / 'base.css').read_text()

STYLE += (ASSETS / 'workspace.css').read_text()

REDIRECT_SCRIPT = "window.location.replace('workspace.html' + window.location.search + window.location.hash);"


def legacy_redirect():
    """Fixed local destination; preserve existing deep links without retaining report data."""
    sh = base64.b64encode(hashlib.sha256(REDIRECT_SCRIPT.encode()).digest()).decode()
    csp = "default-src 'none'; script-src 'sha256-" + sh + "'; base-uri 'none'; form-action 'none'; connect-src 'none'"
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="' + e(csp) + '">'
            '<meta name="referrer" content="no-referrer"><title>Workspace moved · AI Job Skills Lab</title>'
            '</head><body><main><h1>Skills &amp; Learning Workspace</h1>'
            '<p>This report now lives at <a href="workspace.html">workspace.html</a>.</p>'
            '<noscript><p>JavaScript is disabled. Open the link above; to keep a bookmarked lesson, '
            'change only projects.html to workspace.html in the address bar.</p></noscript>'
            '</main><script>' + REDIRECT_SCRIPT + '</script></body></html>')


def e(value):
    return escape(str(value if value is not None else 'Unknown'), quote=True)


def label(value):
    if value == 'role':
        return 'Role family'
    return str(value).replace('_', ' ').replace('-', ' ').capitalize()


def chip(value, tone=''):
    return '<span class="chip ' + tone + '">' + e(value) + '</span>'


def attrs(values):
    return ' '.join('data-' + key + '="' + e(json.dumps(sorted(set(map(str, val))), ensure_ascii=False)) + '"'
                    for key, val in values.items())


def detail(title, value):
    return '<details><summary>' + e(title) + '</summary><pre>' + e(json.dumps(value, ensure_ascii=False, indent=2)) + '</pre></details>'


def report_location(row):
    """Display captured geography without inventing normalized country evidence."""
    country = row.get('country')
    if isinstance(country, str) and country.strip():
        return country.strip(), 'country'
    geography = row.get('segments', {}).get('source_geography')
    if isinstance(geography, str) and geography.strip():
        return geography.strip(), 'source'
    return 'Unknown', 'unknown'


def page(kind, cards, metrics, filters, generated, scope, total, evidence='', tabs=None, workspace=''):
    title = 'Jobs evidence' if kind == 'jobs' else 'Skills & Learning Workspace'
    subtitle = ('Explore the captured engineering requirements behind your research. Availability is recorded at capture, not verified live.'
                if kind == 'jobs' else 'Choose what to learn, practise it through a useful build, and teach from the results. Skills and evidence lead each step.')
    sh = base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
    csp = "default-src 'none'; script-src 'sha256-" + sh + "'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; connect-src 'none'"
    nav = ''.join('<a href="' + k + '.html"' + (' aria-current="page"' if k == kind else '') + '>' + t + '</a>'
                  for k,t in [('jobs','Jobs list'),('workspace','Learning workspace')])
    controls = ''.join('<label>' + e(label(f)) + '<select data-filter="' + f + '"><option value="">All ' + e(label(f).lower()) + '</option></select></label>' for f in filters)
    tabbar = ''
    if tabs:
        tabbar = '<div class="tabs" id="brief-tabs" role="tablist" aria-label="Learning workspace" hidden>' + ''.join(
            '<button type="button" role="tab" id="tab-' + key + '" data-tab="' + key +
            '" data-total="' + str(value['total']) + '" aria-controls="report-results" aria-selected="' +
            ('true' if key == next(iter(tabs)) else 'false') + '" tabindex="' + ('0' if key == next(iter(tabs)) else '-1') +
            '">' + title + ' · ' + str(value['total']) + '</button>'
            for key, value in tabs.items()
            for title in [{'path':'My learning path', 'skill':'Skills', 'project':'Projects', 'youtube':'YouTube experiments', 'progress':'Progress'}[key]]) + '</div>'
    panel = '<div id="report-results"' + (' role="tabpanel" aria-labelledby="tab-' + next(iter(tabs)) + '"' if tabs else '') + '>'
    stats = ''.join('<div class="stat"><strong>' + e(v) + '</strong><span>' + e(k) + '</span></div>' for k,v in metrics)
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="' + e(csp) + '"><meta name="referrer" content="no-referrer"><title>' + e(title) + ' · AI Job Skills Lab</title><style>' + STYLE + '</style></head><body><a class="skip-link" href="#report-results">Skip to content</a><header><nav aria-label="Reports">' + nav + '</nav><div class="brand">AI Job Skills Lab / Research notes</div><h1>' + e(title) + '</h1><p>' + subtitle + '</p><div class="date">GENERATED ' + e(generated[:19].replace('T',' ') + ' UTC') + ' · PRIVATE / OFFLINE</div></header><main><div class="stats">' + stats + '</div><div class="notice">' + e(scope) + '</div>' + tabbar + workspace + '<div class="controls" id="report-controls"><label class="search">Search<input id="search" type="search" placeholder="Type to filter…" autocomplete="off" aria-describedby="search-help" aria-controls="report-results"></label><label>Search in<select id="search-scope"><option value="titles">Titles</option><option value="all">All content, including evidence</option></select></label>' + controls + '<button id="clear" type="button">Clear filters</button></div><p class="meta" id="search-help">Results update as you type. Titles are searched by default; choose All content to include descriptions and evidence.</p><div class="resultbar"><span id="result-count" role="status" aria-live="polite">' + str(len(cards)) + ' displayed</span><span id="available-count">' + str(total) + ' available · ' + str(total-len(cards)) + ' beyond generation limit</span></div><noscript><p>JavaScript is disabled. All generated entries remain readable; search and filters need the bundled offline script.</p></noscript>' + panel + ''.join(cards) + '<div id="no-results" class="empty"' + (' hidden' if cards else '') + '>No matching entries. Clear the filters, or generate suggestions after collecting and analyzing evidence.</div></div>' + evidence + '<footer>Source statements, classifications and model proposals have different evidence strength. Viewing is not acceptance. This is a dated local view; regenerate after new evidence or decisions. Withdrawal removes managed files on the next supported operation; close any stale browser view. Do not publish or copy restricted source content.</footer></main><script>' + SCRIPT + '</script></body></html>'


def render(state, now, limit, *, days=30, basis='capture'):
    snapshot, dependencies = aggregate(state)
    artifacts = state['artifacts']
    jobs = []
    filter_values = {name: set() for name in ('role', 'source', 'location', 'availability')}
    displayed_observations = set()
    openings = sorted(snapshot['openings'], key=lambda g: max(artifacts[k]['payload']['captured_at'] for k in g['observations']), reverse=True)
    for group in openings[:limit]:
        rows = [(k,artifacts[k]['payload']) for k in group['observations']]
        key,row = max(rows, key=lambda item: (item[1]['captured_at'], item[0]))
        sources = [r['source'] for _,r in rows]
        locations = [report_location(r) for _,r in rows]
        analyses = [a['payload'] for analysis_id,a in artifacts.items() if analysis_id in dependencies and a['kind']=='analysis' and a['payload']['observation'] in group['observations']]
        capabilities = sorted({c for a in analyses for claim in a['claims'] for c in claim['capabilities']})
        status = group['availability']
        roles = role_families(row['title'])
        facets = {'role':roles,'source':sources,'location':[value for value, _ in locations],'availability':[status]}
        for name, values in facets.items():
            filter_values[name].update(values)
        location_chips = ''.join(chip('Location unknown' if basis == 'unknown' else value + (' · source location' if basis == 'source' else '')) for value, basis in sorted(set(locations)))
        card = '<article class="card" data-card ' + attrs(facets) + '><div class="eyebrow">' + e(row['employer_name']) + '</div><h2>' + e(row['title']) + '</h2><div class="chips">' + chip(status + ' at capture', 'good' if status=='open' else 'warn') + ''.join(chip(x,'blue') for x in sorted(set(sources))) + location_chips + '</div><div class="meta">Posted ' + e(row['posted_at']) + ' · Captured ' + e(row['captured_at']) + ' · Language: ' + e(row['language']) + '</div><div class="chips" aria-label="Role families suggested by title">' + ''.join(chip(c,'blue') for c in roles) + '</div><div class="chips">' + ''.join(chip(c,'purple') for c in capabilities) + '</div>'
        for observation, captured in rows:
            displayed_observations.add(observation)
            card += '<details id="observation-' + observation + '"><summary>Description · ' + e(captured['source']) + '</summary><p class="prose">' + e(captured['description'] or 'Description not captured. Explicit requirements remain unknown.') + '</p><p>Source URL: ' + e(captured['url']) + '</p><p>Revision: ' + e(captured['source_revision']) + '</p><code>' + e(observation) + '</code></details>'
        card += detail('Extracted requirements and classification', analyses)
        card += detail('Source metadata and limitations', [{k:r[k] for k in ('source','native_id','employer_domain','employer_requisition','segments','availability_evidence','limitations')} for _,r in rows])
        jobs.append(card+'</article>')
    briefs = {k:a['payload'] for k,a in artifacts.items() if a['kind']=='brief' and a['payload']['kind'] in ('project','youtube')}
    revised = {b.get('revises') for b in briefs.values()}
    decisions = {v['brief']:(k,v) for k,v in latest_decisions(state).items()}
    current = [(k,b) for k,b in briefs.items() if k not in revised]
    current.sort(key=lambda item:(item[1].get('created_at',''), item[0]), reverse=True)
    dependencies += list(briefs) + [k for k,v in decisions.values() if v['brief'] in briefs]
    by_kind = {kind: [(key,b) for key,b in current if b['kind'] == kind] for kind in ('project','youtube')}
    rendered = {'project': [], 'youtube': []}
    selected = [item for kind in by_kind for item in by_kind[kind][:limit]]
    for key,brief in selected:
        kind = brief['kind']
        proposal=brief.get('proposal',{})
        disposition=proposal.get('disposition','unknown'); decision=decisions.get(key,(None,{}))[1].get('decision','unreviewed')
        caps=proposal.get('capabilities',[])
        card='<article id="brief-'+key+'" class="card '+kind+'" data-card data-kind="'+kind+'" '+attrs({'disposition':[disposition],'decision':[decision],'capability':caps})+'><div class="eyebrow">'+('PROJECT BRIEF' if kind == 'project' else 'YOUTUBE EXPERIMENT')+' / REVISION '+e(brief.get('revision',1))+'</div><h2>'+e(proposal.get('title','Project draft' if kind == 'project' else 'YouTube experiment draft'))+'</h2><div class="chips">'+chip(disposition,'good' if disposition in ('propose','contribute') else 'warn')+chip(decision,'blue')+''.join(chip(c,'purple') for c in caps)+'</div>'
        if brief.get('learning_path'):
            card += '<p><a href="#path-' + e(brief['learning_path']) + '" data-jump="path">Open the shared learning path</a></p>'
        if proposal:
            card+='<details class="brief-body"><summary>Read the experiment and implementation plan</summary><div class="section-grid">'+''.join('<section><h3>'+e(label(name))+'</h3><p class="prose">'+e(value)+'</p></section>' for name,value in proposal.get('sections',{}).items())+'</div></details>'
            card+=detail('Separate assessments and prerequisites', {'judgments':proposal.get('judgments',{}),'prerequisites':proposal.get('prerequisites',[])})
        else:
            card+='<p class="prose">'+e(brief.get('markdown','No structured proposal available.'))+'</p>'
        limits=proposal.get('limitations',[])+brief.get('evidence_limits',[])
        card+='<div class="limits"><strong>Evidence limits</strong><ul>'+''.join('<li>'+e(x)+'</li>' for x in dict.fromkeys(limits))+'</ul></div>'
        card+='<details><summary>Captured evidence and inspected alternatives</summary>'
        for claim in proposal.get('market_claims',[])+proposal.get('context_claims',[]):
            card+='<blockquote>'+e(claim['quote'])+'</blockquote><code>'+e(claim.get('analysis',claim.get('context')))+'</code>'
        for alternative in proposal.get('alternatives',[]):
            context=artifacts[alternative['context']]['payload']
            card+=detail('Inspected alternative', {'reason':alternative['reason'],'context':context})
        card+=detail('Brief provenance', {k:v for k,v in brief.items() if k in ('snapshot','contexts','versions','created_at','source_scope','notice')})
        card+='</details></article>'
        rendered[kind].append(card)
    scope=snapshot['scope']+'. Sample evidence only; no worldwide coverage or demand-growth claim.'
    evidence=detail('Collection coverage, queries, filters and limitations', snapshot)
    evidence+=detail('Report role grouping', {'version':ROLE_VERSION,'basis':'Latest displayed title only; English keyword rules, multiple families allowed. Not validated responsibilities, AI relevance or market classification.'})
    counts=snapshot['counts']
    useful_filters = [name for name, values in filter_values.items() if values - {'Unknown', 'unknown', '', OTHER}]
    scope+=' Role families are title-based navigation hints; they can overlap and do not validate AI responsibilities. Location uses captured country or the source-provided geography, which may describe a region or multiple countries. Location and availability filters appear when captured values are known.'
    tabs = {kind: {'shown': len(rendered[kind]), 'total': len(by_kind[kind])} for kind in by_kind}
    from tools.research_learning_reports import cards as learning_cards
    learning, totals, learning_deps, skills, cited = learning_cards(state, now, limit, days=days, basis=basis, brief_ids={key for key,_ in selected})
    dependencies += learning_deps
    shown_paths = set(re.findall(r'id="path-([0-9a-f]{64})"', ''.join(learning['path'])))
    for kind in rendered:
        for i,card in enumerate(rendered[kind]):
            for path_id in re.findall(r'href="#path-([0-9a-f]{64})"',card):
                if path_id not in shown_paths:
                    card = card.replace('<a href="#path-'+path_id+'" data-jump="path">Open the shared learning path</a>', 'Shared learning path is outside the displayed selection. Inspect it through Codex.')
            rendered[kind][i]=card
    # Learning paths can cite an older retained revision, or a job outside this
    # page's card limit. Keep those exact sources reachable without counting them
    # as extra openings or current vacancies.
    for oid in sorted(cited - displayed_observations):
        captured = artifacts[oid]['payload']; dependencies.append(oid)
        evidence += '<details id="observation-' + oid + '"><summary>Cited description outside the displayed jobs list · ' + e(captured['title']) + '</summary><p class="meta">Historical or outside the card limit; not an additional opening. Captured: ' + e(captured['captured_at']) + '</p><p class="prose">' + e(captured['description'] or 'Description unavailable.') + '</p><p>Source: ' + e(captured['url']) + '</p></details>'
    jobs_html=page('jobs',jobs,[('Deduplicated openings',len(openings)),('Verified employer domains',counts['distinct_verified_employer_domains']),('Missing descriptions',counts['missing_descriptions']),('Captured revisions',counts['captured_revisions'])],useful_filters,now,scope,len(openings),evidence)
    all_tabs = {'path': {'shown':len(learning['path']), 'total':totals['path']},
                'skill': {'shown':len(learning['skill']), 'total':totals['skill']}, **tabs,
                'progress': {'shown':len(learning['progress']), 'total':totals['progress']}}
    skill_counts = skills['counts']
    learning_evidence = detail('Skills window, analysis coverage and limitations',
        {k: skills[k] for k in ('counts','period','collection_days','limitations')})
    # Product hypotheses remain secondary and do not weight learning priorities.
    products = {k:a['payload'] for k,a in artifacts.items() if a['kind']=='brief' and a['payload']['kind']=='product'}
    dependencies += list(products)
    if products: learning_evidence += detail('Secondary product hypotheses — unvalidated', products)
    learning_scope = ('Last ' + str(days) + ' days · ' + basis + ' dates · ' +
        str(skill_counts.get('analysed_openings',0)) + ' openings with detailed analysis; ' +
        str(skill_counts.get('pending_or_legacy_openings',0)) + ' pending or legacy. ' +
        str(len(skills['collection_days'])) + ' collection dates observed. Counts describe the analysed sample, not worldwide demand. ' +
        'Use Codex to select a path and record progress. No browser action records completion.')
    if not learning['path']:
        learning_evidence = '<p class="notice">Start in Skills, inspect the evidence, then ask Codex to propose a path for chosen skill IDs. No connected learning path has been generated yet.</p>' + learning_evidence
    workspace_html=page('workspace',learning['path']+learning['skill']+rendered['project']+rendered['youtube']+learning['progress'],
        [('Catalog skills',sum(s['normalization'] != 'unresolved' for s in skills.get('skills',{}).values())),('Analysed AI openings',skill_counts.get('in_domain_denominator',0)),
         ('Project briefs',len(by_kind['project'])),('YouTube experiments',len(by_kind['youtube']))],
        ['topic','category','disposition','decision','basis'],now, learning_scope,
        sum(t['total'] for t in all_tabs.values()), evidence=learning_evidence, tabs=all_tabs, workspace=learning['intro'])
    return {'jobs.html':jobs_html,'workspace.html':workspace_html,'projects.html':legacy_redirect()}, sorted(set(dependencies)), {
        'jobs':{'shown':len(jobs),'total':len(openings)},'projects':tabs['project'],'youtube':tabs['youtube']}
