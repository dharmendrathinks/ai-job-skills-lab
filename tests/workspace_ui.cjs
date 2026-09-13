// Deterministic DOM behavior tests. No browser, network, application state or npm dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');
let document;
class Element {
  constructor(tag, attrs={}, text='') {
    this.tagName=tag.toUpperCase();this.attrs={};this.dataset={};this.children=[];this.events={};this.text=text;
    this.value='';this.hidden=false;this.open=false;this.options=[];this.parentElement=null;
    Object.entries(attrs).forEach(([key,value])=>this.setAttribute(key,value));
  }
  setAttribute(key,value) {
    this.attrs[key]=String(value);
    if(key==='id') this.id=String(value);
    if(key==='class') this.className=String(value);
    if(key.startsWith('data-')) this.dataset[key.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=String(value);
  }
  getAttribute(key){return this.attrs[key]??null;}
  append(child){
    if(child.parentElement) child.remove();
    child.parentElement=this;this.children.push(child);
    if(this.tagName==='SELECT')this.options.push(child);
  }
  remove(index){
    if(index!==undefined){this.options.splice(index,1);this.children.splice(index,1);return;}
    if(this.parentElement){const p=this.parentElement;p.children=p.children.filter(c=>c!==this);this.parentElement=null;}
  }
  get textContent(){return this.text+this.children.map(c=>c.textContent).join(' ');}
  set textContent(text){this.text=String(text);this.children=[];}
  addEventListener(event,callback){this.events[event]=callback;}
  matches(selector){
    if(selector.startsWith('['))return this.getAttribute(selector.slice(1,-1))!==null;
    if(selector.startsWith('.'))return (this.className||'').split(' ').includes(selector.slice(1));
    return this.tagName===selector.toUpperCase();
  }
  querySelectorAll(selector){
    if(selector.startsWith(':scope > '))return this.children.filter(c=>c.matches(selector.slice(9)));
    return this.children.flatMap(c=>[...(c.matches(selector)?[c]:[]),...c.querySelectorAll(selector)]);
  }
  querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
  closest(selector){let p=this;while(p){if(p.matches(selector))return p;p=p.parentElement;}return null;}
  focus(){document.activeElement=this;}
  select(){this.selected=true;}
  scrollIntoView(){this.scrolled=true;}
}
function fixture(hash='') {
  const body=new Element('body');
  const add=(parent,tag,attrs={},text='')=>{const e=new Element(tag,attrs,text);parent.append(e);return e;};
  document={body,querySelectorAll:s=>body.querySelectorAll(s),createElement:t=>new Element(t),
    getElementById:id=>{const walk=p=>p.id===id?p:p.children.map(walk).find(Boolean);return walk(body);}};
  const controls=add(body,'div',{id:'report-controls'});
  add(controls,'input',{id:'search'});
  const scope=add(controls,'select',{id:'search-scope'});scope.value='titles';
  add(controls,'button',{id:'clear'});
  const filterParent=add(controls,'label');
  const filter=add(filterParent,'select',{'data-filter':'category'});add(filter,'option',{value:''});
  add(body,'p',{id:'search-help'});
  const bar=add(body,'div');add(bar,'span',{id:'result-count'});add(bar,'span',{id:'available-count'});
  const tabs=add(body,'div',{id:'brief-tabs'});
  for(const [kind,total] of [['path',1],['skill',4],['project',1],['youtube',0],['progress',0]])
    add(tabs,'button',{id:'tab-'+kind,'data-tab':kind,'data-total':total},kind);
  add(body,'section',{'data-tab-section':'path'});
  const skillSection=add(body,'section',{'data-tab-section':'skill'});
  const label=add(skillSection,'label');const view=add(label,'select',{id:'skill-view'});view.value='browse';
  const sortLabel=add(skillSection,'label');const sort=add(sortLabel,'select',{id:'skill-sort'});sort.value='grouped';
  add(skillSection,'p',{id:'skill-view-help'});
  const results=add(body,'div',{id:'report-results'});
  const path=add(results,'article',{'data-card':'','data-kind':'path',id:'curriculum-owned'});add(path,'h2',{},'Owned curriculum');
  const enclosing=add(path,'details');
  const lessons=add(enclosing,'div');
  const one=add(lessons,'details',{'data-lesson':'',id:'lesson-one'});one.open=true;add(one,'h3',{},'One');
  const two=add(lessons,'details',{'data-lesson':'',id:'lesson-two'});add(two,'h3',{},'Two');
  const skill=(id,title,frequency,topic,order,mode='browse')=>{
    const e=add(results,'article',{'data-card':'','data-kind':'skill','data-skill-view':mode,id,
      'data-frequency':frequency,'data-topic-order':order,'data-topic-label':topic,'data-category':'["technology"]'});
    add(e,'h2',{},title);add(e,'p',{},'Owned evidence');return e;
  };
  const python=skill('skill-python','Python',2,'Foundations',0);
  const sql=skill('skill-sql','SQL',2,'Foundations',0);
  const rag=skill('skill-rag','Retrieval',5,'Retrieval and data',1);
  const unknown=skill('skill-unresolved','A new source phrase',7,'Source terms',99,'terms');
  const trend=add(results,'article',{'data-card':'','data-kind':'skill','data-skill-view':'trends',id:'trend'});add(trend,'h2',{},'Observed change');
  const project=add(results,'article',{'data-card':'','data-kind':'project',id:'brief-owned'});add(project,'h2',{},'Owned experiment');
  const link=add(project,'a',{'data-jump':'path',href:'#lesson-two'},'Open lesson');
  const handoff=add(project,'details',{class:'handoff'});
  const field=add(handoff,'textarea');field.value='A named request with an internal reference.';
  const copy=add(handoff,'button',{'data-copy':''});const status=add(handoff,'span',{class:'copy-status'});
  add(results,'div',{id:'no-results'});
  const location={_hash:hash,get hash(){return this._hash},set hash(v){this._hash=v.startsWith('#')?v:'#'+v}};
  const window={location,events:{},addEventListener(n,fn){this.events[n]=fn;}};
  const navigator={clipboard:{writeText:async()=>{throw new Error('Unavailable for file URLs');}}};
  vm.runInNewContext(source,{document,window,navigator});
  return {document,window,python,sql,rag,unknown,trend,view,sort,project,one,two,enclosing,copy,field,status,filter,link,results};
}
(async()=>{
  let f=fixture('#skill-unresolved');
  assert.equal(f.view.value,'terms');assert.equal(f.unknown.hidden,false);assert.equal(f.python.hidden,true);
  assert.equal(f.document.getElementById('tab-skill').attrs['aria-selected'],'true');
  assert.equal(f.document.activeElement,f.unknown);
  f.view.value='browse';f.view.events.change();
  const names=()=>f.results.children.filter(c=>c.dataset.kind==='skill'&&!c.hidden).map(c=>c.querySelector('h2').textContent);
  assert.deepEqual(names(),['Python','SQL','Retrieval']);
  assert.deepEqual(f.document.querySelectorAll('[data-group-heading]').map(e=>e.textContent),['Foundations','Retrieval and data']);
  f.sort.value='frequency';f.sort.events.change();assert.deepEqual(names(),['Retrieval','Python','SQL']);
  f.sort.value='alphabetical';f.sort.events.change();assert.deepEqual(names(),['Python','Retrieval','SQL']);
  const search=f.document.getElementById('search');search.value='sql';search.events.input();assert.deepEqual(names(),['SQL']);
  f.document.getElementById('clear').events.click();assert.equal(names().length,3);
  f.view.value='trends';f.view.events.change();assert.equal(f.trend.hidden,false);assert.equal(f.python.hidden,true);
  assert.equal(f.document.getElementById('report-controls').hidden,true);
  f.window.location.hash='#lesson-two';f.window.events.hashchange();
  assert.equal(f.two.open,true);assert.equal(f.enclosing.open,true);assert.equal(f.two.scrolled,true);
  f.two.events.toggle();assert.equal(f.one.open,false);
  f.window.location.hash='#brief-owned';f.window.events.hashchange();assert.equal(f.project.hidden,false);
  await f.copy.events.click();assert.equal(f.field.selected,true);assert.match(f.status.textContent,/keyboard/);
  f.window.location.hash='#skill-python';f.window.events.hashchange();assert.equal(f.view.value,'browse');assert.equal(f.python.hidden,false);
  f.window.location.hash='#brief-owned';f.window.events.hashchange();assert.equal(f.project.hidden,false); // Back/forward route.
  f.window.location.hash='#%E0%A4%A';assert.doesNotThrow(()=>f.window.events.hashchange());
  f=fixture('#lesson-two');assert.equal(f.two.open,true);assert.equal(f.enclosing.open,true); // Reload into collapsed content.
  console.log('Grouping, sorting, subviews, deep links, reload, Back, lesson disclosure and clipboard fallback passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
