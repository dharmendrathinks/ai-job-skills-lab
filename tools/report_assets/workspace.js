(() => {
  const all = selector => [...(document.querySelectorAll(selector) || [])];
  const cards = all('[data-card]');
  const search = document.getElementById('search');
  const scope = document.getElementById('search-scope');
  const selects = all('[data-filter]');
  const tabs = all('[data-tab]');
  const view = document.getElementById('skill-view');
  const sort = document.getElementById('skill-sort');
  const values = (card, name) => JSON.parse(card.getAttribute('data-' + name) || '[]');
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  const texts = cards.map(card => normalize(card.textContent));
  const titles = cards.map(card => normalize(card.querySelector('h2').textContent));
  let activeKind = tabs.length ? tabs[0].dataset.tab : null;
  const activeCards = () => cards.filter(card => (!activeKind || card.dataset.kind === activeKind) &&
    (activeKind !== 'skill' || !view || !card.dataset.skillView || card.dataset.skillView === view.value));
  function populateFilters() {
    selects.forEach(select => {
      while (select.options.length > 1) select.remove(1);
      const options = [...new Set(activeCards().flatMap(card => values(card, select.dataset.filter)))].sort();
      options.forEach(value => { const option = document.createElement('option');
        option.value = value; option.textContent = value.replaceAll('-', ' '); select.append(option); });
      select.value = '';
      if (select.parentElement) select.parentElement.hidden = options.length === 0;
    });
  }
  function orderSkills() {
    all('[data-group-heading]').forEach(h => h.remove());
    if (activeKind !== 'skill' || !sort || !view || view.value === 'trends') return;
    const rows = activeCards().filter(c => !c.hidden);
    const name = c => normalize(c.querySelector('h2').textContent);
    rows.sort((a,b) => (sort.value === 'grouped' ? Number(a.dataset.topicOrder) - Number(b.dataset.topicOrder) : 0) ||
      (sort.value !== 'alphabetical' ? Number(b.dataset.frequency) - Number(a.dataset.frequency) : 0) || name(a).localeCompare(name(b)));
    const parent = document.getElementById('report-results');
    let previous = null;
    rows.forEach(card => {
      if (sort.value === 'grouped' && card.dataset.topicLabel !== previous) {
        const heading = document.createElement('h2'); heading.setAttribute('data-group-heading', '');
        heading.className = 'group-heading'; heading.textContent = card.dataset.topicLabel;
        parent.append(heading); previous = card.dataset.topicLabel;
      }
      parent.append(card);
    });
    parent.append(document.getElementById('no-results'));
  }
  function update() {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    const active = new Set(activeCards());
    let shown = 0;
    cards.forEach((card, i) => {
      const match = active.has(card) && terms.every(term => (scope.value === 'all' ? texts[i] : titles[i]).includes(term)) &&
        selects.every(select => !select.value || values(card, select.dataset.filter).includes(select.value));
      card.hidden = !match; shown += Number(match);
    });
    document.getElementById('result-count').textContent = `${shown} of ${active.size} displayed`;
    document.getElementById('no-results').hidden = shown !== 0;
    all('[data-tab-section]').forEach(section => { section.hidden = section.dataset.tabSection !== activeKind; });
    const controls = document.getElementById('report-controls');
    const hideControls = activeKind === 'path' || activeKind === 'progress' || (activeKind === 'skill' && view?.value === 'trends');
    if (controls) controls.hidden = hideControls;
    const searchHelp = document.getElementById('search-help');
    if (searchHelp) searchHelp.hidden = hideControls;
    const resultbar = document.getElementById('result-count').parentElement;
    if (resultbar) resultbar.hidden = activeKind === 'path' || activeKind === 'progress';
    if (tabs.length) {
      const selected = tabs.find(tab => tab.dataset.tab === activeKind);
      const loaded = cards.filter(card => card.dataset.kind === activeKind && card.dataset.skillView !== 'trends').length;
      document.getElementById('available-count').textContent = `${selected.dataset.total} available in this tab · ${Math.max(0,Number(selected.dataset.total) - loaded)} beyond generation limit`;
    }
    if (sort) sort.parentElement.hidden = view.value === 'trends';
    const help = document.getElementById('skill-view-help');
    if (help) help.textContent = view.value === 'terms' ? 'Source phrases stay visible while their meaning and aliases are reviewed. They are not yet catalog skills.' :
      view.value === 'trends' ? 'Change indicators require compatible collection, analysis and normalization across both windows.' :
      'Counts describe this analysed sample. Learning topics are editorial navigation, not a priority score.';
    orderSkills();
  }
  function reset() { search.value = ''; scope.value = 'titles'; selects.forEach(s => {s.value = '';}); }
  function selectTab(tab, navigate=false) {
    activeKind = tab.dataset.tab;
    tabs.forEach(item => { item.setAttribute('aria-selected', String(item === tab)); item.tabIndex = item === tab ? 0 : -1; });
    document.getElementById('report-results').setAttribute('aria-labelledby', tab.id);
    reset(); populateFilters(); update();
    if (navigate && typeof window !== 'undefined' && window.location.hash !== '#' + tab.id) window.location.hash = tab.id;
  }
  search.addEventListener('input', update); search.addEventListener('search', update);
  scope.addEventListener('change', update);
  selects.forEach(select => select.addEventListener('change', update));
  document.getElementById('clear').addEventListener('click', () => { reset(); update(); search.focus(); });
  if (view) view.addEventListener('change', () => { reset(); populateFilters(); update(); });
  if (sort) sort.addEventListener('change', update);
  tabs.forEach((tab,index) => {
    tab.addEventListener('click', () => selectTab(tab,true));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); selectTab(tabs[next],true); tabs[next].focus(); }
    });
  });
  all('[data-jump]').forEach(link => link.addEventListener('click', () => {
    const tab = tabs.find(t => t.dataset.tab === link.dataset.jump); if (tab) selectTab(tab);
  }));
  function revealHash() {
    if (typeof window === 'undefined' || !window.location.hash) return;
    let id; try { id = decodeURIComponent(window.location.hash.slice(1)); } catch (_) { return; }
    const target = document.getElementById(id); if (!target) return;
    const directTab = tabs.find(t => t.id === id);
    if (directTab) { selectTab(directTab); return; }
    const card = target.closest('[data-card]');
    const section = target.closest('[data-tab-section]');
    const kind = card?.dataset.kind || section?.dataset.tabSection;
    const tab = tabs.find(t => t.dataset.tab === kind);
    if (tab) selectTab(tab); else {reset(); update();}
    if (card?.dataset.skillView && view) {view.value = card.dataset.skillView; populateFilters(); update();}
    let ancestor = target;
    while (ancestor) { if (ancestor.tagName === 'DETAILS') ancestor.open = true; ancestor = ancestor.parentElement; }
    target.setAttribute('tabindex', '-1'); target.focus({preventScroll:true}); target.scrollIntoView({block:'start'});
  }
  all('[data-lesson]').forEach(lesson => lesson.addEventListener('toggle', () => {
    if (!lesson.open) return;
    const siblings = lesson.parentElement.querySelectorAll(':scope > [data-lesson]');
    siblings.forEach(other => { if (other !== lesson) other.open = false; });
  }));
  function prepareProgress(container) {
    const summary = container.querySelector('.progress-summary').value.trim();
    const status = container.querySelector('.copy-status');
    if (!summary) {
      status.textContent = 'Describe what you tried and the actual result first.';
      container.querySelector('.progress-summary').focus();
      return false;
    }
    const event = container.querySelector('.progress-event').value;
    container.querySelector('.prepared-request').value =
      `Help me record ${event} for ${container.dataset.title}.\n` +
      `Path reference: ${container.dataset.path}\nLesson: ${container.dataset.lesson}\n` +
      `My account of the work:\n${summary}\n\n` +
      'Treat this account as self-reported unless you inspect reproduced evidence. Ask when it happened and clarify missing conditions. ' +
      'For completion, compare the actual result with the lesson completion check. Review the current record before saving, then regenerate the workspace report. ' +
      'Do not infer mastery or change my profile.';
    status.textContent = 'Request prepared. Review it, then copy it to Codex. Progress is not saved here.';
    return true;
  }
  all('[data-prepare-progress]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => prepareProgress(button.closest('.handoff')));
  });
  all('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const container = button.closest('.handoff');
    if (container.hasAttribute('data-progress-request') && !prepareProgress(container)) return;
    const field = container.querySelector('.prepared-request') || container.querySelector('textarea');
    const status = container.querySelector('.copy-status');
    try {
      if (typeof navigator === 'undefined' || !navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(field.value); status.textContent = 'Copied. Paste into Codex.';
    } catch (_) { field.focus(); field.select(); status.textContent = 'Request selected. Use your keyboard to copy it.'; }
  }));
  if (tabs.length) {document.getElementById('brief-tabs').hidden = false; selectTab(tabs[0]);}
  else {populateFilters();update();}
  if (typeof window !== 'undefined') {window.addEventListener('hashchange', revealHash); revealHash();}
})();
