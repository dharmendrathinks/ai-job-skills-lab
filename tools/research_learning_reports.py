"""Learning workspace presentation over immutable records; browser actions never write state."""
from tools.research_skills import skill_payload
from tools.research_curricula import library, topics, safe_url


def handoff(request, label='Copy request for Codex'):
    from tools.research_reports import e
    return ('<details class="handoff"><summary>' + e(label) + '</summary><p>Copy this request into Codex. '
            'Review and save changes there, then regenerate this report.</p><textarea readonly aria-label="Request for Codex">' +
            e(request) + '</textarea><button type="button" data-copy>Copy request</button>'
            '<span role="status" aria-live="polite" class="copy-status"></span></details>')


def resource_card(resource, *, optional=False):
    from tools.research_reports import e
    title = e(resource['title'])
    link = '<a href="' + e(resource['url']) + '" target="_blank" rel="noopener noreferrer">' + title + ' ↗</a>' if safe_url(resource['url']) else title
    return '<div class="resource"><span class="eyebrow">' + ('GO DEEPER' if optional else 'READ THIS SECTION') + '</span><h4>' + link + '</h4><p><strong>' + e(resource['section']) + '</strong></p><p>' + e(resource['why']) + '</p><p class="meta">Checked ' + e(resource['checked_on']) + ' · ' + e(resource['access']) + '</p></div>'


def lesson_view(lessons, resources, prefix, *, current=None, progress=None):
    from tools.research_reports import e
    progress = progress or {}
    nav = '<nav class="syllabus" aria-label="Lesson syllabus"><span class="eyebrow">YOUR SYLLABUS</span><ol>'
    panels = ''
    for i, m in enumerate(lessons, 1):
        target = prefix + '-' + m['id']; done = progress.get(m['id'], {}).get('event') == 'completed'
        nav += '<li><a href="#' + e(target) + '">' + e(m['title']) + '</a><small>' + ('Recorded complete' if done else str(m['hours_min']) + '–' + str(m['hours_max']) + ' hours') + '</small></li>'
        panels += '<details class="lesson" data-lesson id="' + e(target) + '"' + (' open' if m['id'] == (current or lessons[0]['id']) else '') + '><summary><span class="eyebrow">LESSON ' + str(i) + ' / ' + str(len(lessons)) + '</span><h3>' + e(m['title']) + '</h3><span class="meta">' + str(m['hours_min']) + '–' + str(m['hours_max']) + ' hours estimated</span></summary><div class="lesson-body"><p class="objective">' + e(m['objective']) + '</p><p>' + e(m['explanation']) + '</p>'
        if m.get('prerequisites'): panels += '<p class="meta">Builds on: ' + e(', '.join(next(l['title'] for l in lessons if l['id'] == pre) for pre in m['prerequisites'])) + '</p>'
        panels += '<h4>Worked example</h4><pre class="example"><code>' + e(m['example']) + '</code></pre><h4>Try it yourself</h4><p>' + e(m['exercise']) + '</p>'
        panels += ''.join(resource_card(resources[r], optional=j > 0) for j,r in enumerate(m['resources']))
        panels += '<div class="completion-check"><h4>Ready to move on when…</h4><p>' + e(m['completion_check']) + '</p><p><strong>You’ll have:</strong> ' + e(m['artifact']) + '</p></div>'
        if progress.get(m['id']):
            event = progress[m['id']]
            panels += '<p class="notice">Recorded ' + e(event['event']) + ' · ' + e(event['basis']) + ': ' + e(event['summary']) + '</p>'
        panels += '</div></details>'
    return '<div class="lesson-layout">' + nav + '</ol></nav><div class="lessons">' + panels + '</div></div>'


def curriculum_card(path, resources):
    from tools.research_reports import e, chip
    hours = [sum(m[k] for m in path['lessons']) for k in ('hours_min', 'hours_max')]
    identity = 'curriculum-' + path['id']
    return ('<article class="card path curriculum" id="' + identity + '" data-card data-kind="path">'
        '<div class="eyebrow">CURATED PATH · ' + e(path['level']) + '</div><h2>' + e(path['title']) + '</h2><p class="lead">' + e(path['summary']) + '</p>'
        '<div class="chips">' + chip(str(len(path['lessons'])) + ' lessons') + chip(str(hours[0]) + '–' + str(hours[1]) + ' hours estimated', 'blue') + '</div>'
        '<p><strong>You’ll build:</strong> ' + e(path['outcome']) + '</p><p class="meta">' + e(' '.join(path['prerequisites'])) + '</p>'
        '<details class="curriculum-body"><summary>Explore the syllabus and lessons</summary>' + lesson_view(path['lessons'], resources, identity) + '</details>'
        + handoff('Propose a learning path from the '+path['title']+' curriculum ('+path['id']+'). Use research_decisions path-propose --curriculum '+path['id']+'. Ask about my goals and available time before adapting it. Do not select it or record progress until I choose.', 'Plan this learning path with Codex')
        + '<p class="meta">' + e(path['editorial_status']) + ' · Resource links require internet; lessons and examples read offline.</p></article>')


def introductions(snapshot, book, active=False):
    from tools.research_reports import e
    topic_data = topics()
    roadmap = '<section class="workspace-intro" data-tab-section="path"><div class="section-heading"><span class="eyebrow">A ROADMAP, AT YOUR PACE</span><h2>Build something you can explain.</h2><p>Start with a focused project. Learn its foundations, test its behavior, and keep the evidence of your work.</p></div><details class="roadmap"><summary>Explore the AI engineering roadmap</summary><p>Editorial prerequisite order. Frequency in job descriptions does not determine learning order.</p><ol class="topic-grid">'
    for t in topic_data['topics']:
        title = {x['id']:x['title'] for x in topic_data['topics']}
        roadmap += '<li><strong>' + e(t['title']) + '</strong><p>' + e(t['description']) + '</p><small>' + e('Builds on: ' + ', '.join(title[k] for k in t['prerequisites']) if t['prerequisites'] else 'Start here') + '</small></li>'
    roadmap += '</ol></details><details class="foundations" id="foundations"><summary>Refresh the foundations · Python, JSON, APIs and testing</summary>' + lesson_view(book['foundations']['lessons'], book['resources'], 'foundation') + '</details></section>'
    if active:
        start = roadmap.index('<div class="section-heading">')
        end = roadmap.index('</div>',start)+6
        roadmap = roadmap[:start]+roadmap[end:]
    counts = snapshot['counts']; known = sum(s['normalization'] != 'unresolved' for s in snapshot.get('skills', {}).values())
    skills = '<section class="workspace-intro" data-tab-section="skill"><div class="section-heading"><span class="eyebrow">THE SKILL EXPLORER</span><h2>What are teams asking for?</h2><p>Explore skills independently of a learning path. Follow a count back to the captured job requirements.</p></div><p class="coverage-line"><strong>' + str(known) + ' catalog skills</strong> · ' + str(len(snapshot.get('skills', {})) - known) + ' source terms awaiting review · ' + str(counts.get('in_domain_denominator',0)) + ' analysed AI openings</p><div class="skill-toolbar"><label>View<select id="skill-view"><option value="browse">Browse skills</option><option value="trends">Trends</option><option value="terms">Observed terms</option></select></label><label>Sort<select id="skill-sort"><option value="grouped">Topic, then frequency</option><option value="frequency">Frequency across topics</option><option value="alphabetical">Name A–Z</option></select></label></div><p class="meta" id="skill-view-help">Counts describe this analysed sample. Learning topics are editorial navigation.</p></section>'
    return roadmap + skills


def trend_card(state, snapshot):
    from tools.research_reports import e
    histories = [(k,a['payload']) for k,a in state['artifacts'].items() if a['kind'] == 'skill-history']
    histories.sort(key=lambda kv:(kv[1].get('windows',[{}])[-1].get('period',{}).get('to',''),kv[0]), reverse=True)
    compatible = [(k,p) for k,p in histories if p.get('basis',p.get('windows',[{}])[-1].get('period',{}).get('basis')) == snapshot.get('period',{}).get('basis')]
    if not compatible:
        return '<article class="card trends" data-card data-kind="skill" data-skill-view="trends"><h2>Trends need a comparable history</h2><p>There are no managed skill comparisons for this date basis yet. Browse current observations while collection history develops.</p><p class="meta">Compare adjacent 30-day windows using a reviewed cohort. Missing, partial or changed collection cannot establish a trend.</p>' + handoff('Inspect research collection coverage and prepare a skill-history comparison for two adjacent 30-day windows. Use the existing cohort checks; do not treat missing or partial collection as growth.') + '</article>', []
    key,p = compatible[0]
    html = '<article class="card trends" data-card data-kind="skill" data-skill-view="trends"><h2>Skill observations over time</h2><p>Historical comparison · ' + e(p.get('status')) + '</p>'
    for i,w in enumerate(p['windows'],1):
        html += '<p><strong>Window ' + str(i) + ':</strong> ' + e(w['period']['from'][:10]) + ' → ' + e(w['period']['to'][:10]) + ' · ' + str(w['counts']['in_domain_denominator']) + ' analysed AI openings · ' + str(len(w['collection_days'])) + ' collection dates</p>'
    if p.get('change_indicators') is not None:
        html += '<p>Change in observed share, in percentage points. This is a comparison within this sample.</p><div class="table-scroll"><table><thead><tr><th>Skill</th><th>Previous</th><th>Current</th><th>Change</th></tr></thead><tbody>'
        for change in p['change_indicators']:
            html += '<tr><th>' + e(change['name']) + '</th><td>' + e(str(change['previous'])+' / '+str(p['windows'][0]['counts']['in_domain_denominator'])) + '</td><td>' + e(str(change['current'])+' / '+str(p['windows'][1]['counts']['in_domain_denominator'])) + '</td><td>' + format(change['percentage_points'], '+.1f') + ' pp</td></tr>'
        html += '</tbody></table></div>'
    else: html += '<p class="notice">Change indicators unavailable. ' + e(p.get('limitation','Collection or analysis is not comparable.')) + '</p>'
    if p.get('demo_unavailable_example'): html += '<details><summary>Example: when a trend is unavailable</summary><p>'+e(p['demo_unavailable_example'])+'</p></details>'
    if p.get('issues'): html += '<ul>' + ''.join('<li>'+e(i)+'</li>' for i in p['issues']) + '</ul>'
    return html + '</article>', [key]


def cards(state, now, limit, *, days=30, basis='capture', brief_ids=None):
    from tools.research_reports import e, chip, attrs, detail
    from tools.research_evidence import timestamp
    from tools.research_learning import path_decisions
    arts = state['artifacts']; result = {'path': [], 'skill': [], 'progress': []}
    deps = []; totals = {k: 0 for k in result}; cited_observations = set(); book = library()
    if 'domain_pack' not in state:
        snapshot, deps = skill_payload(state, timestamp(now), days=days, basis=basis)
        denominator = snapshot['counts']['in_domain_denominator']
        topic_data = topics(); topic_map = {t['id']:t for t in topic_data['topics']}
        totals['skill'] = len(snapshot['skills'])
        for sid, s in list(snapshot['skills'].items())[:limit]:
            unreviewed = s['normalization'] == 'unresolved'
            topic = topic_data['assignments'].get(sid)
            group = topic_map[topic]['title'] if topic else 'Source terms awaiting review'
            rank = list(topic_map).index(topic) if topic else 99
            card = '<article class="card skill" id="skill-' + e(sid) + '" data-card data-kind="skill" data-skill-view="' + ('terms' if unreviewed else 'browse') + '" data-frequency="' + str(s['openings']) + '" data-topic-order="' + str(rank) + '" data-topic-label="' + e(group) + '" ' + attrs({'category': [s['kind']], 'normalization': [s['normalization']], 'topic':[group], 'capability': s['capabilities']}) + '><div class="skill-heading"><div><div class="eyebrow">' + e(group) + ' / ' + e(s['kind']) + '</div><h2>' + e(s['name']) + '</h2></div><div class="skill-frequency"><strong>' + str(s['openings']) + '<span> / ' + str(denominator) + '</span></strong><small>analysed openings</small></div></div><p class="skill-definition">' + e(s['definition'] if not unreviewed else 'Exact source wording. Its meaning and catalog mapping still need review.') + '</p>'
            old_ids = {snapshot['evidence'][eid].get('original_skill_id', sid) for eid in s['evidence']} - {sid}
            card += ''.join('<span id="skill-'+e(old)+'" aria-hidden="true"></span>' for old in sorted(old_ids))
            card += '<details class="skill-details"><summary>Explore evidence and learning</summary><div class="chips">' + chip(str(s['openings']) + ' of ' + str(denominator) + ' analysed in-domain openings', 'purple') + chip(str(round(s['share'] * 100,1)) + '% of this analysed slice' if s['share'] is not None else 'Share unknown', 'blue') + '</div><p class="meta">' + ' · '.join(e(k.capitalize()) + ': ' + str(v) for k,v in s['modalities'].items()) + '</p><p class="meta">' + str(s['reported_employers']) + ' reported employer names · ' + str(s['verified_employers']) + ' verified employer identities. Requirement categories can overlap.</p>'
            related = [snapshot['skills'][k]['name'] + ' (' + str(v) + ')' for k,v in sorted(s['cooccurs'].items(), key=lambda x:(-x[1],x[0]))[:8]]
            card += '<p><strong>Appears alongside:</strong> ' + e(', '.join(related) or 'No observed co-occurrence') + '</p>'
            matches = [p for p in book['paths'] if sid in p['skills']]
            if matches:
                card += '<h3>Practise through a project</h3><ul>' + ''.join('<li><a href="#curriculum-' + p['id'] + '" data-jump="path">' + e(p['title']) + '</a></li>' for p in matches) + '</ul>'
            card += '<details><summary>What the jobs actually request · ' + str(len(s['evidence'])) + ' evidence spans</summary>'
            for eid in s['evidence'][:20]:
                ev = snapshot['evidence'][eid]; cited_observations.add(ev['observation'])
                card += '<blockquote>' + e(ev['quote']) + '</blockquote><p class="meta">' + e(ev['employer']) + ' · ' + e(ev['title']) + ' · ' + e(ev['modality']) + '</p><a href="jobs.html#observation-' + ev['observation'] + '">Inspect captured description</a>'
            if len(s['evidence']) > 20: card += '<p>Showing the first 20 spans; all spans remain in the managed skill snapshot.</p>'
            card += '</details>' + handoff(('Review the source wording and mapping for ' if unreviewed else 'Help me explore learning paths for ') + s['name'] + '. Research skill reference: ' + sid + '. Inspect current evidence before proposing work.', 'Review this term with Codex' if unreviewed else 'Explore this skill with Codex')
            card += detail('Technical provenance', {'skill':sid, 'normalization':s['normalization'], 'catalog':snapshot['catalog_revision']}) + '</details></article>'
            result['skill'].append(card)
    else:
        snapshot = {'counts':{}, 'period':{}, 'skills':{}, 'collection_days':[], 'limitations':['Fine-grained AI skills and curricula are unavailable in this domain workspace.']}
    paths = {k:a['payload'] for k,a in arts.items() if a['kind'] == 'learning-path'}
    decisions = path_decisions(state)
    selections = [a['payload'] for a in arts.values() if a['kind'] == 'learning-selection']
    active = max(selections, key=lambda p:p.get('selected_at',''), default={}).get('path')
    progress = [(k,a['payload']) for k,a in arts.items() if a['kind'] == 'learning-progress']
    corrected = {p['supersedes'] for _,p in progress}
    progress = [(k,p) for k,p in progress if k not in corrected]
    eligible = {k:p for k,p in paths.items() if k not in decisions or decisions[k][1]['decision'] == 'deferred' and timestamp(decisions[k][1]['defer_until']) <= timestamp(now)}
    selected = sorted(eligible.items(), key=lambda kv:(kv[0] != active, kv[1]['created_at'],kv[0]))
    totals['path'] = len(eligible)
    for key,row in selected[:min(limit, 1 if active in eligible else 3)]:
        p = row['proposal']; events = [(k,v) for k,v in progress if v['path'] == key]
        by_milestone = {m['id']:max([v for _,v in events if v['milestone'] == m['id']],key=lambda v:v['recorded_at'],default={}) for m in p['milestones']}
        next_step = next((m for m in p['milestones'] if by_milestone[m['id']].get('event') != 'completed'),None)
        source_snapshot = arts.get(row.get('skill_snapshot'),{}).get('payload',{})
        names = source_snapshot.get('skills',{})
        card = '<article class="card path active-path" id="path-' + key + '" data-card data-kind="path"><div class="eyebrow">' + ('ACTIVE LEARNING PATH' if key == active else 'YOUR DRAFT / REVIEW BEFORE SELECTING') + '</div><h2>' + e(p['title']) + '</h2><p class="lead">' + e(p['experiment']) + '</p><div class="chips">' + ''.join(chip(names.get(s,{}).get('name',s),'purple') for s in p['skills']) + '</div>'
        done = sum(v.get('event') == 'completed' for v in by_milestone.values())
        card += '<p class="meta">' + str(done) + ' of ' + str(len(p['milestones'])) + ' milestones recorded complete · ' + ('Selected effort' if key == active else 'Selection pending') + '</p>'
        next_action = next_step['implement'] if next_step else 'All milestones explicitly recorded complete. Review the evidence and prepare an optional walkthrough.'
        if p['disposition'] == 'insufficient-evidence': next_action = 'Insufficient evidence for a path. Inspect the limitations before proposing work.'
        card += '<div class="next-action"><span class="eyebrow">NEXT PRACTICAL STEP</span><p>' + e(next_action) + '</p></div><details><summary>Prerequisites, relevance and assumptions</summary><p>' + e(p['why_now']) + '</p><ul>' + ''.join('<li>'+e(s)+'</li>' for s in p['prerequisites']) + '</ul>' + detail('Assumptions and evidence limits', p['assumptions'] + p['limitations'] + row['selection_limits']) + '</details>'
        if row.get('adaptation'):
            adaptation = row['adaptation']
            card += '<details><summary>Adapted to your goals · review pending</summary><p>'+e(adaptation['project_context'])+'</p><ul>'+''.join('<li>'+e(item['emphasis'])+'</li>' for item in adaptation['lesson_emphasis'])+'</ul></details>'
        if row.get('curriculum'):
            card += lesson_view(row['curriculum']['lessons'], row['resource_library'], 'path-'+key, current=next_step['id'] if next_step else None, progress=by_milestone)
        else:
            for index,m in enumerate(p['milestones'],1):
                card += '<details class="lesson" data-lesson id="path-' + key + '-' + e(m['id']) + '"' + (' open' if next_step and next_step['id'] == m['id'] else '') + '><summary><span class="eyebrow">MILESTONE ' + str(index) + '</span><h3>' + e(m['title']) + '</h3><span class="meta">' + str(m['hours_min']) + '–' + str(m['hours_max']) + ' hours</span></summary><div class="lesson-body"><p class="objective">' + e(m['understand']) + '</p><h4>Build</h4><p>' + e(m['implement']) + '</p><div class="completion-check"><h4>Check yourself</h4><p>' + e(m['self_check']) + '</p><p><strong>You’ll have:</strong> ' + e(m['artifact']) + '</p></div><h4>Test and compare</h4><p>' + e(m['tests']) + '</p>'
                for rid in m['resources']:
                    ctx = arts[rid]['payload']; url = ctx['locator']
                    card += resource_card({'title':'Inspected supporting source','url':url,'section':ctx['inspection_depth'],'why':'Supporting material for this historical draft; inspect its fit before using it as a lesson.','checked_on':ctx.get('captured_at','Unknown')[:10],'access':'External source.'})
                if not m['resources']: card += '<p class="meta">This historical draft has no inspected lesson resource. Explore the curated paths below for a complete syllabus.</p>'
                card += '<details><summary>What this work demonstrates</summary><p>' + e(m['demonstrates']) + '</p><p>' + e(m['does_not_demonstrate']) + '</p></details></div></details>'
        if p['market_evidence']:
            card += '<details><summary>Why these skills — captured job evidence</summary>'
            for eid in p['market_evidence']:
                ev = source_snapshot['evidence'][eid]; cited_observations.add(ev['observation'])
                card += '<blockquote>' + e(ev['quote']) + '</blockquote><p class="meta">' + e(ev['employer']) + ' · ' + e(ev['title']) + '</p><a href="jobs.html#observation-' + ev['observation'] + '">Inspect the captured description</a>'
            card += '</details>'
        card += '<p><strong>Optional teaching question:</strong> ' + e(p['teaching_question']) + '</p>'
        for bid,a in arts.items():
            b=a['payload']
            if a['kind']=='brief' and b.get('learning_path')==key:
                if brief_ids is not None and bid not in brief_ids:
                    card += '<p class="meta">Linked '+e(b['kind'])+' is outside this report’s display limit. Regenerate with a higher limit to inspect it.</p>'
                    continue
                card += '<p><a href="#brief-'+bid+'" data-jump="'+e(b['kind'])+'">'+e(b['kind'].capitalize()+': '+b['proposal']['title'])+'</a></p>'
        action = 'inspect the limitations of' if p['disposition']=='insufficient-evidence' else 'record progress for' if key==active else 'select'
        card += handoff('Help me '+action+' '+p['title']+'. Research path reference: '+key+'. Review the current state and my actual work before saving anything.') + '</article>'
        result['path'].append(card)
    legacy = [(k,a['payload']) for k,a in arts.items() if a['kind']=='brief' and a['payload']['kind']=='learning']
    if not paths:
        for key,b in legacy[:min(3,limit)]:
            p=b.get('proposal',{}); result['path'].append('<article class="card path" data-card data-kind="path"><div class="eyebrow">HISTORICAL LEARNING DRAFT</div><h2>'+e(p.get('title','Learning draft'))+'</h2>'+detail('Learning practice and prerequisites',p.get('sections',{}))+'</article>')
        totals['path']=len(legacy)
    if 'domain_pack' not in state:
        curated = [curriculum_card(p,book['resources']) for p in book['paths']]
        result['path'] = result['path'] + curated if active else curated + result['path']
        totals['path'] += len(book['paths'])
        trends, history_deps = trend_card(state,snapshot)
        result['skill'].append(trends); deps += history_deps
        result['intro'] = introductions(snapshot,book,active=bool(active))
    else: result['intro'] = ''
    totals['progress']=len(progress)
    for key,p in sorted(progress,key=lambda kv:kv[1]['recorded_at'],reverse=True)[:limit]:
        exists=p['path'] in paths
        title = next((m['title'] for m in paths[p['path']]['proposal']['milestones'] if m['id']==p['milestone']),p['milestone']) if exists else p['milestone']
        result['progress'].append('<article class="card progress" data-card data-kind="progress" '+attrs({'category':[p['event']],'basis':[p['basis']]})+'><div class="eyebrow">'+e(p['basis'])+'</div><h2>'+e(p['event'].capitalize()+': '+title)+'</h2><p>'+e(p['summary'])+'</p><p class="meta">'+e(p['occurred_at'])+'</p><p>'+('Linked learning path available.' if exists else 'Market justification unavailable or withdrawn; independently sourced work record retained.')+'</p>'+detail('Conditions and inspected results',{'conditions':p['conditions'],'quotes':p['result_quotes'],'evidence':p['evidence']})+'</article>')
    if not progress:
        result['intro'] += '<section class="workspace-intro" data-tab-section="progress"><h2>Your work, with evidence.</h2><p>No progress recorded yet. Select a path, try its first exercise, then record what happened through Codex. Attempts and failures belong here too.</p></section>'
    deps += [k for k,a in arts.items() if a['kind'] in ('learning-path','learning-selection','learning-decision')]
    deps += [k for k,_ in progress]+[k for k,_ in legacy]
    return result,totals,deps,snapshot,cited_observations
