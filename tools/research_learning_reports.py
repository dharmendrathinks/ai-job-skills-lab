"""Readable learning cards over managed records, with no browser writes."""
from tools.research_skills import skill_payload


def cards(state, now, limit, *, days=30, basis='capture'):
    from tools.research_reports import e, chip, attrs, detail
    from tools.research_evidence import timestamp
    arts = state['artifacts']; result = {'path': [], 'skill': [], 'progress': []}
    deps = []; totals = {k: 0 for k in result}; cited_observations = set()
    if 'domain_pack' not in state:
        snapshot, deps = skill_payload(state, timestamp(now), days=days, basis=basis)
        denominator = snapshot['counts']['in_domain_denominator']
        totals['skill'] = len(snapshot['skills'])
        for sid, s in list(snapshot['skills'].items())[:limit]:
            card = '<article class="card skill" id="skill-' + e(sid) + '" data-card data-kind="skill" ' + attrs({'category': [s['kind']], 'normalization': [s['normalization']], 'capability': s['capabilities']}) + '><div class="eyebrow">SKILL EVIDENCE / ' + e(s['kind']) + '</div><h2>' + e(s['name']) + '</h2><p>' + e(s['definition']) + '</p>'
            card += '<div class="chips">' + chip(str(s['openings']) + ' of ' + str(denominator) + ' analysed in-domain openings', 'purple')
            card += chip(str(round(s['share'] * 100, 1)) + '% of this analysed slice' if s['share'] is not None else 'Share unknown', 'blue')
            card += chip(s['normalization'], 'warn' if s['normalization'] == 'unresolved' else 'good') + '</div>'
            card += '<p class="meta">' + ' · '.join(e(k.capitalize()) + ': ' + str(v) for k,v in s['modalities'].items()) + '</p>'
            card += '<p>' + str(s['reported_employers']) + ' reported employer names · ' + str(s['verified_employers']) + ' verified employer identities</p>'
            related = [snapshot['skills'][k]['name'] + ' (' + str(v) + ')' for k,v in sorted(s['cooccurs'].items(), key=lambda x: -x[1])[:8]]
            card += '<p><strong>Appears alongside:</strong> ' + e(', '.join(related) or 'No observed co-occurrence') + '</p>'
            card += '<details><summary>What the jobs actually request · ' + str(len(s['evidence'])) + ' evidence spans</summary>'
            for eid in s['evidence'][:20]:
                ev = snapshot['evidence'][eid]
                cited_observations.add(ev['observation'])
                card += '<blockquote>' + e(ev['quote']) + '</blockquote><p class="meta">' + e(ev['employer']) + ' · ' + e(ev['title']) + ' · ' + e(ev['modality']) + '</p><a href="jobs.html#observation-' + ev['observation'] + '">Inspect captured description</a>'
                if ev['section_context']: card += '<p class="meta">Section context: ' + e(ev['section_context']) + '</p>'
            if len(s['evidence']) > 20: card += '<p>Showing the first 20 spans; all spans remain in the managed skill snapshot.</p>'
            card += '</details><p class="notice">To practise this skill, ask Codex to propose a learning path for skill <code>' + e(sid) + '</code>. Market frequency is separate from your learning priority.</p></article>'
            result['skill'].append(card)
    else:
        snapshot = {'counts': {}, 'period': {}, 'collection_days': [], 'limitations': ['Fine-grained skill catalog is currently qualified for the default AI workspace only.']}
    paths = {k:a['payload'] for k,a in arts.items() if a['kind'] == 'learning-path'}
    from tools.research_learning import path_decisions
    decisions = path_decisions(state)
    selections = [a['payload']['path'] for a in arts.values() if a['kind'] == 'learning-selection']
    active = selections[0] if selections else None
    progress = [(k,a['payload']) for k,a in arts.items() if a['kind'] == 'learning-progress']
    corrected = {p['supersedes'] for _,p in progress}
    progress = [(k,p) for k,p in progress if k not in corrected]
    eligible = {k:p for k,p in paths.items() if k not in decisions or
                decisions[k][1]['decision'] == 'deferred' and timestamp(decisions[k][1]['defer_until']) <= timestamp(now)}
    selected = sorted(eligible.items(), key=lambda kv: (kv[0] != active, kv[1]['created_at'], kv[0]))
    totals['path'] = len(eligible)
    for key, row in selected[:min(limit, 1 if active else 3)]:
        p = row['proposal']; events = [(k,v) for k,v in progress if v['path'] == key]
        by_milestone = {m['id']: max([v for _,v in events if v['milestone'] == m['id']], key=lambda v:v['recorded_at'], default={}) for m in p['milestones']}
        next_step = next((m for m in p['milestones'] if by_milestone[m['id']].get('event') != 'completed'), None)
        skill_names = arts[row['skill_snapshot']]['payload']['skills']
        card = '<article class="card path" id="path-' + key + '" data-card data-kind="path"><div class="eyebrow">' + ('ACTIVE LEARNING PATH' if key == active else 'LEARNING OPTION / HUMAN REVIEW PENDING') + '</div><h2>' + e(p['title']) + '</h2><p>' + e(p['why_now']) + '</p><p><strong>Experiment:</strong> ' + e(p['experiment']) + '</p><div class="chips">' + ''.join(chip(skill_names[s]['name'], 'purple') for s in p['skills']) + '</div>'
        next_action = e(next_step['self_check']) if next_step else 'All milestones explicitly recorded complete. Review the evidence and prepare the teaching experiment; completion alone is not mastery.'
        if p['disposition'] == 'insufficient-evidence': next_action = 'Insufficient evidence for a path. Review the limitations and inspect the missing resources before proposing work.'
        card += '<p class="notice"><strong>Next action:</strong> ' + next_action + '</p>'
        card += '<p><strong>Prerequisites to check:</strong> ' + e('; '.join(p['prerequisites']) or 'Use the practical self-checks; no skill mastery assumed.') + '</p>'
        card += '<details><summary>Why these skills — captured job evidence</summary>'
        source_snapshot = arts[row['skill_snapshot']]['payload']
        for eid in p['market_evidence']:
            ev = source_snapshot['evidence'][eid]
            cited_observations.add(ev['observation'])
            card += '<blockquote>' + e(ev['quote']) + '</blockquote><p class="meta">' + e(ev['employer']) + ' · ' + e(ev['title']) + '</p><a href="jobs.html#observation-' + ev['observation'] + '">Inspect the captured description</a>'
        card += '</details>'
        for index, m in enumerate(p['milestones'], 1):
            card += '<section class="milestone"><h3>' + str(index) + '. ' + e(m['title']) + '</h3><p class="meta">' + str(m['hours_min']) + '–' + str(m['hours_max']) + ' hours assumed · Milestone ' + e(m['id']) + '</p><div class="section-grid">'
            for k, label in [('understand','Understand'), ('implement','Build'), ('self_check','Check yourself'), ('artifact','Useful artifact'), ('tests','Test and compare'), ('demonstrates','What this can demonstrate'), ('does_not_demonstrate','Limits')]:
                card += '<section><h3>' + label + '</h3><p class="prose">' + e(m[k]) + '</p></section>'
            card += '</div><p><strong>Inspected resources:</strong></p>'
            for resource in m['resources']:
                ctx = arts[resource]['payload']; card += '<p>' + e(ctx['locator']) + ' · ' + e(ctx['inspection_depth']) + '</p>'
            if not m['resources']: card += '<p class="meta">Resource inspection pending. No learning link has been invented.</p>'
            milestone_events = [v for _,v in events if v['milestone'] == m['id']]
            if milestone_events:
                latest = max(milestone_events, key=lambda v:v['recorded_at'])
                card += '<p class="notice">Latest recorded ' + e(latest['event']) + ' (' + e(latest['basis']) + '): ' + e(latest['summary']) + '</p>'
            else: card += '<p class="meta">No progress recorded. Start with this milestone’s self-check.</p>'
            card += '</section>'
        linked = [(k,a['payload']) for k,a in arts.items() if a['kind'] == 'brief' and a['payload'].get('learning_path') == key]
        card += '<p><strong>Teaching question:</strong> ' + e(p['teaching_question']) + '</p>'
        for bid, b in linked: card += '<p><a href="#brief-' + bid + '" data-jump="' + e(b['kind']) + '">' + e(b['kind'].capitalize() + ': ' + b['proposal']['title']) + '</a></p>'
        card += detail('Assumptions and evidence limits', p['assumptions'] + p['limitations'] + row['selection_limits'])
        action = 'inspect the limitations of' if p['disposition'] == 'insufficient-evidence' else ('record progress for' if key == active else 'select')
        card += '<p class="notice">Ask Codex to ' + action + ' path <code>' + key + '</code>. Viewing is not selection, completion or demonstrated ability.</p></article>'
        result['path'].append(card)
    # Historical standalone learning drafts remain reachable rather than being discarded.
    legacy = [(k,a['payload']) for k,a in arts.items() if a['kind'] == 'brief' and a['payload']['kind'] == 'learning']
    if not paths:
        for key, b in legacy[:min(3, limit)]:
            p = b.get('proposal', {})
            result['path'].append('<article class="card path" data-card data-kind="path"><div class="eyebrow">STANDALONE LEARNING DRAFT / NOT A CONNECTED PATH</div><h2>' + e(p.get('title', 'Learning draft')) + '</h2>' + detail('Learning practice and prerequisites', p.get('sections', {})) + '<p>Ask Codex to propose a connected path from the Skills tab.</p></article>')
        totals['path'] = len(legacy)
    totals['progress'] = len(progress)
    for key, p in sorted(progress, key=lambda kv:kv[1]['recorded_at'], reverse=True)[:limit]:
        exists = p['path'] in paths
        result['progress'].append('<article class="card progress" data-card data-kind="progress" ' + attrs({'category':[p['event']], 'basis':[p['basis']]}) + '><div class="eyebrow">' + e(p['basis']) + '</div><h2>' + e(p['event'].capitalize() + ': ' + p['milestone']) + '</h2><p class="prose">' + e(p['summary']) + '</p><p class="meta">' + e(p['occurred_at']) + '</p><p>' + ('Linked learning path available.' if exists else 'Market justification unavailable or withdrawn; independently sourced work record retained.') + '</p>' + detail('Conditions and inspected results', {'conditions':p['conditions'], 'quotes':p['result_quotes'], 'evidence':p['evidence']}) + '</article>')
    deps += [k for k,a in arts.items() if a['kind'] in ('learning-path', 'learning-selection', 'learning-progress', 'learning-decision')]
    deps += [k for k,_ in legacy]
    return result, totals, deps, snapshot, cited_observations
