"""Offline presentation only. Untrusted text never becomes markup or script."""
import base64
import hashlib
from html import escape
import json

from tools.research_evidence import aggregate
from tools.research_outcomes import latest_decisions
from tools.research_report_roles import role_families, VERSION as ROLE_VERSION, OTHER

SCRIPT = r'''(() => {
  const cards = [...document.querySelectorAll('[data-card]')];
  const search = document.getElementById('search');
  const scope = document.getElementById('search-scope');
  const selects = [...document.querySelectorAll('[data-filter]')];
  const values = (card, name) => JSON.parse(card.getAttribute('data-' + name) || '[]');
  const tabs = [...document.querySelectorAll('[data-tab]')];
  let activeKind = tabs.length ? tabs[0].dataset.tab : null;
  const activeCards = () => cards.filter(card => !activeKind || card.dataset.kind === activeKind);
  function populateFilters() {
    selects.forEach(select => {
      while (select.options.length > 1) select.remove(1);
      const options = [...new Set(activeCards().flatMap(card => values(card, select.dataset.filter)))].sort();
      options.forEach(value => { const option = document.createElement('option');
        option.value = value; option.textContent = value; select.append(option); });
      select.value = '';
      if (select.parentElement) select.parentElement.hidden = options.length === 0;
    });
  }
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  const texts = cards.map(card => normalize(card.textContent));
  const titles = cards.map(card => normalize(card.querySelector('h2').textContent));
  function update() {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach((card, i) => {
      const match = (!activeKind || card.dataset.kind === activeKind) && terms.every(term => (scope.value === 'all' ? texts[i] : titles[i]).includes(term)) && selects.every(select =>
        !select.value || values(card, select.dataset.filter).includes(select.value));
      card.hidden = !match; shown += Number(match);
    });
    document.getElementById('result-count').textContent = `${shown} of ${activeCards().length} displayed`;
    document.getElementById('no-results').hidden = shown !== 0;
    if (tabs.length) {
      const selected = tabs.find(tab => tab.dataset.tab === activeKind);
      document.getElementById('available-count').textContent = `${selected.dataset.total} available in this tab · ${Number(selected.dataset.total) - activeCards().length} beyond generation limit`;
    }
  }
  search.addEventListener('input', update);
  search.addEventListener('search', update);
  scope.addEventListener('change', update);
  selects.forEach(select => select.addEventListener('change', update));
  document.getElementById('clear').addEventListener('click', () => {
    search.value = ''; scope.value = 'titles'; selects.forEach(select => { select.value = ''; }); update(); search.focus();
  });
  function selectTab(tab) {
    activeKind = tab.dataset.tab;
    tabs.forEach(item => {
      item.setAttribute('aria-selected', String(item === tab));
      item.tabIndex = item === tab ? 0 : -1;
    });
    document.getElementById('report-results').setAttribute('aria-labelledby', tab.id);
    search.value = ''; scope.value = 'titles'; populateFilters(); update();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); selectTab(tabs[next]); tabs[next].focus(); }
    });
  });
  document.querySelectorAll('[data-jump]').forEach(link => link.addEventListener('click', () => {
    const tab = tabs.find(t => t.dataset.tab === link.dataset.jump); if (tab) selectTab(tab);
  }));
  if (tabs.length) {
    document.getElementById('brief-tabs').hidden = false;
    selectTab(tabs[0]);
  } else { populateFilters(); update(); }
})();'''

STYLE = '''
:root{color-scheme:light;--ink:#18243c;--muted:#5a687e;--line:#dce3ef;--violet:#6846d8;--cyan:#067c8a}
*{box-sizing:border-box}body{margin:0;background:#f1f4fa;color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{background:linear-gradient(115deg,#101b32,#26365b 65%,#174452);color:#fff;padding:28px max(24px,calc((100vw - 1180px)/2)) 36px}
.brand{font:700 12px ui-monospace,SFMono-Regular,monospace;letter-spacing:.16em;text-transform:uppercase;color:#95e3e0}
nav{display:flex;gap:8px;float:right}nav a{font-size:13px;color:#e2e9ff;border:1px solid #526181;text-decoration:none;padding:6px 14px;border-radius:8px}nav a[aria-current]{background:#e3dcff;color:#352063;border-color:#e3dcff}
h1{font-size:clamp(30px,4vw,46px);letter-spacing:-.045em;line-height:1.12;margin:30px 0 12px;font-weight:750}header p{max-width:760px;color:#c4d0e6;margin:0}header .date{font:12px ui-monospace,monospace;color:#a9bbd7;margin-top:18px}
main{max-width:1228px;margin:auto;padding:24px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}.stat{background:#fff;border:1px solid var(--line);border-top:3px solid var(--violet);padding:18px 22px;border-radius:12px;box-shadow:0 4px 14px #162b4b05}.stat:nth-child(2){border-top-color:#08959d}.stat:nth-child(3){border-top-color:#d69922}.stat:nth-child(4){border-top-color:#4884d8}.stat strong{display:block;font-size:28px;letter-spacing:-.05em;line-height:1.3}.stat span{font-size:12px;color:var(--muted)}
.controls{display:flex;gap:10px;align-items:end;flex-wrap:wrap;padding:18px;background:#fff;border:1px solid var(--line);border-radius:12px;margin:22px 0 12px;position:sticky;top:8px;z-index:2;box-shadow:0 5px 24px #192b4e0a}label{display:flex;flex-direction:column;gap:5px;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}label.search{flex:1;min-width:200px}input,select,button{font:inherit;font-size:14px;border:1px solid #cbd5e4;border-radius:7px;padding:10px 12px;background:#fff;color:var(--ink);min-height:42px;max-width:100%}select{max-width:220px}button{cursor:pointer;background:#eee9ff;color:#4b3199;border-color:#d8ccff;font-weight:650}input:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #139da5;outline-offset:3px}
.resultbar{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin:12px 2px 20px}.card{background:#fff;border:1px solid var(--line);border-radius:14px;margin:0 0 16px;padding:24px 28px;box-shadow:0 6px 24px #20345105;border-left:4px solid #5e62cc}.card.project{border-left-color:#07989b}.card.youtube{border-left-color:#d75b69}.card.path{border-left-color:#6846d8}.card.skill{border-left-color:#1685ba}.card.progress{border-left-color:#c48c22}.milestone{margin-top:24px;padding-top:12px;border-top:2px solid #e2e6f0}.milestone>h3{font-size:19px;letter-spacing:-.02em}.card.youtube .eyebrow{color:#ad384c}.tabs{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0 0}.tabs button{background:white;color:var(--muted);border-color:var(--line)}.tabs button[aria-selected="true"]{background:#e3f4f2;color:#075f64;border-color:#52b1af}.tabs button[data-tab="youtube"][aria-selected="true"]{background:#fff0f2;color:#a32e43;border-color:#db8390}.eyebrow{color:var(--cyan);font:600 12px ui-monospace,monospace;letter-spacing:.03em}.card h2{font-size:23px;line-height:1.35;letter-spacing:-.025em;margin:7px 0 10px;overflow-wrap:anywhere}.chips{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0}.chip{font-size:11px;padding:3px 9px;border-radius:5px;background:#eef1f7;color:#526077}.chip.good{background:#e1f4ee;color:#15634a}.chip.warn{background:#fff2d8;color:#845e13}.chip.purple{background:#ede8ff;color:#573b9e}.chip.blue{background:#e2f2fa;color:#1b6683}
.meta{color:var(--muted);font-size:12px}.prose{white-space:pre-wrap;overflow-wrap:anywhere}.section-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px 28px;margin-top:20px}.section-grid section{border-top:1px solid var(--line);padding-top:12px}.section-grid h3{font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:#5a428f;margin:0 0 8px}.section-grid p{margin:0;font-size:14px}.notice{border:1px solid #d9d6f1;background:#f3f0fc;padding:13px 17px;border-radius:9px;font-size:13px;color:#544879}.limits{color:#79571b;background:#fffaee;border-radius:8px;padding:12px 16px;font-size:13px;margin-top:18px}.limits ul{margin:4px 0;padding-left:20px}
details{border-top:1px solid var(--line);padding-top:12px;margin-top:18px}summary{cursor:pointer;font-weight:650;font-size:13px;color:#4e6182}details p{font-size:13px}pre{font:12px/1.6 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fb;padding:14px;border-radius:7px;max-height:440px;overflow:auto}code{font:11px ui-monospace,monospace;overflow-wrap:anywhere}blockquote{margin:12px 0;padding:10px 16px;border-left:3px solid #80cacc;background:#f1faf9;font-size:13px}.empty{padding:36px;text-align:center;border:1px dashed #a9b8cd;border-radius:12px;background:#fff;color:var(--muted)}footer{margin:30px 0 12px;font-size:12px;color:var(--muted)}[hidden]{display:none!important}
@media(max-width:760px){header{padding:22px}.brand{display:block;padding-bottom:14px}nav{float:none}main{padding:16px}.stats{grid-template-columns:1fr 1fr}.section-grid{grid-template-columns:1fr}.card{padding:20px}.controls{position:static}label{flex:1;min-width:135px}select{max-width:100%;width:100%}.resultbar{gap:12px}.stat{padding:14px}}
@media print{header{background:#fff;color:#18243c}header p,header .date{color:#526077}.controls,nav{display:none}.card{break-inside:avoid;box-shadow:none}main{max-width:none}}
'''


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


def page(kind, cards, metrics, filters, generated, scope, total, evidence='', tabs=None):
    title = 'Jobs evidence' if kind == 'jobs' else 'Learn, build & teach'
    subtitle = ('Explore the captured engineering requirements behind your research. Availability is recorded at capture, not verified live.'
                if kind == 'jobs' else 'Choose what to learn, practise it through a useful build, and teach from the results. Skills and evidence lead each step.')
    sh = base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
    csp = "default-src 'none'; script-src 'sha256-" + sh + "'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; connect-src 'none'"
    nav = ''.join('<a href="' + k + '.html"' + (' aria-current="page"' if k == kind else '') + '>' + t + '</a>'
                  for k,t in [('jobs','Jobs list'),('projects','Learning workspace')])
    controls = ''.join('<label>' + e(label(f)) + '<select data-filter="' + f + '"><option value="">All ' + e(label(f).lower()) + '</option></select></label>' for f in filters)
    tabbar = ''
    if tabs:
        tabbar = '<div class="tabs" id="brief-tabs" role="tablist" aria-label="Brief type" hidden>' + ''.join(
            '<button type="button" role="tab" id="tab-' + key + '" data-tab="' + key +
            '" data-total="' + str(value['total']) + '" aria-controls="report-results" aria-selected="' +
            ('true' if key == next(iter(tabs)) else 'false') + '" tabindex="' + ('0' if key == next(iter(tabs)) else '-1') +
            '">' + title + ' · ' + str(value['total']) + '</button>'
            for key, value in tabs.items()
            for title in [{'path':'My learning path', 'skill':'Skills', 'project':'Projects', 'youtube':'YouTube experiments', 'progress':'Progress'}[key]]) + '</div>'
    panel = '<div id="report-results"' + (' role="tabpanel" aria-labelledby="tab-' + next(iter(tabs)) + '"' if tabs else '') + '>'
    stats = ''.join('<div class="stat"><strong>' + e(v) + '</strong><span>' + e(k) + '</span></div>' for k,v in metrics)
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="' + e(csp) + '"><meta name="referrer" content="no-referrer"><title>' + title + ' · AI Job Skills Lab</title><style>' + STYLE + '</style></head><body><header><nav aria-label="Reports">' + nav + '</nav><div class="brand">AI Job Skills Lab / Research notes</div><h1>' + title + '</h1><p>' + subtitle + '</p><div class="date">GENERATED ' + e(generated) + ' · PRIVATE / OFFLINE</div></header><main><div class="stats">' + stats + '</div><div class="notice">' + e(scope) + '</div>' + tabbar + '<div class="controls"><label class="search">Search<input id="search" type="search" placeholder="Type to filter…" autocomplete="off" aria-describedby="search-help" aria-controls="report-results"></label><label>Search in<select id="search-scope"><option value="titles">Titles</option><option value="all">All content, including evidence</option></select></label>' + controls + '<button id="clear" type="button">Clear filters</button></div><p class="meta" id="search-help">Results update as you type. Titles are searched by default; choose All content to include descriptions and evidence.</p><div class="resultbar"><span id="result-count" role="status" aria-live="polite">' + str(len(cards)) + ' displayed</span><span id="available-count">' + str(total) + ' available · ' + str(total-len(cards)) + ' beyond generation limit</span></div><noscript><p>JavaScript is disabled. All generated entries remain readable; search and filters need the bundled offline script.</p></noscript>' + panel + ''.join(cards) + '<div id="no-results" class="empty"' + (' hidden' if cards else '') + '>No matching entries. Clear the filters, or generate suggestions after collecting and analyzing evidence.</div></div>' + evidence + '<footer>Source statements, classifications and model proposals have different evidence strength. Viewing is not acceptance. This is a dated local view; regenerate after new evidence or decisions. Withdrawal removes managed files on the next supported operation; close any stale browser view. Do not publish or copy restricted source content.</footer></main><script>' + SCRIPT + '</script></body></html>'


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
            card+='<div class="section-grid">'+''.join('<section><h3>'+e(label(name))+'</h3><p class="prose">'+e(value)+'</p></section>' for name,value in proposal.get('sections',{}).items())+'</div>'
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
        card+='</details><p class="meta">Draft · '+e(key)+'</p></article>'
        rendered[kind].append(card)
    scope=snapshot['scope']+'. Sample evidence only; no worldwide coverage or demand-growth claim.'
    evidence=detail('Collection coverage, queries, filters and limitations', snapshot)
    evidence+=detail('Report role grouping', {'version':ROLE_VERSION,'basis':'Latest displayed title only; English keyword rules, multiple families allowed. Not validated responsibilities, AI relevance or market classification.'})
    counts=snapshot['counts']
    useful_filters = [name for name, values in filter_values.items() if values - {'Unknown', 'unknown', '', OTHER}]
    scope+=' Role families are title-based navigation hints; they can overlap and do not validate AI responsibilities. Location uses captured country or the source-provided geography, which may describe a region or multiple countries. Location and availability filters appear when captured values are known.'
    tabs = {kind: {'shown': len(rendered[kind]), 'total': len(by_kind[kind])} for kind in by_kind}
    from tools.research_learning_reports import cards as learning_cards
    learning, totals, learning_deps, skills, cited = learning_cards(state, now, limit, days=days, basis=basis)
    dependencies += learning_deps
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
    projects_html=page('projects',learning['path']+learning['skill']+rendered['project']+rendered['youtube']+learning['progress'],
        [('Specific skills',totals['skill']),('Analysed AI openings',skill_counts.get('in_domain_denominator',0)),
         ('Project briefs',len(by_kind['project'])),('YouTube experiments',len(by_kind['youtube']))],
        ['category','normalization','capability','disposition','decision','basis'],now, learning_scope,
        sum(t['total'] for t in all_tabs.values()), evidence=learning_evidence, tabs=all_tabs)
    return {'jobs.html':jobs_html,'projects.html':projects_html}, sorted(set(dependencies)), {
        'jobs':{'shown':len(jobs),'total':len(openings)},'projects':tabs['project'],'youtube':tabs['youtube']}
