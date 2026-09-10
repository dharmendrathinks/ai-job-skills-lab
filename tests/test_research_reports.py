"""Report separation, hostile content and managed checkout-copy lifecycle."""
import base64
from datetime import timedelta
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.research_evidence import Store
from tools.research_operations import report
from tools.research_report_files import bind, directory
from tools.research_reports import SCRIPT, report_location
from tools.research_report_roles import role_families, OTHER
from tests.test_research_evidence import bundle, NOW


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve(); self.repo=self.root/'repo'; self.repo.mkdir()
        subprocess.run(['git','init','-q',str(self.repo)],check=True)
        (self.repo/'.gitignore').write_text('reports/\n')
        self.now=NOW; self.store=Store(self.root/'private',clock=lambda:self.now)
        self.obs=self.store.import_bundle(bundle())['observations'][0]

    def brief(self,kind='project',number=1):
        with self.store.transaction() as state:
            return self.store.put(state,'brief',{'kind':kind,'revision':number,'revises':None,
                'markdown':'UNTRUSTED </script><img src=x onerror=alert(1)>',
                'proposal':{'title':'Build <unsafe> & useful','disposition':'insufficient-evidence',
                'capabilities':['retrieval-knowledge'],'sections':{'problem':'A concrete problem.'},
                'limitations':['No inspected alternative.']}},[self.obs])

    def test_two_views_project_only_and_deduplicated_jobs(self):
        self.brief(); self.brief('learning'); self.brief('product')
        duplicate=bundle('second-source'); self.store.import_bundle(duplicate)
        result=report(self.store)
        self.assertEqual(result['jobs']['total'],1)
        self.assertEqual(result['projects']['total'],1)
        jobs=Path(result['jobs']['path']).read_text(); projects=Path(result['projects']['path']).read_text()
        self.assertIn('AI engineer',jobs); self.assertNotIn('Build &lt;unsafe&gt;',jobs)
        self.assertIn('Build &lt;unsafe&gt; &amp; useful',projects)
        self.assertIn('synthetic test corpus',jobs)
        self.assertNotIn('research-profile',projects)

    def test_unknown_filters_hidden_then_known_values_exposed(self):
        data=bundle('unknown','unknown-job')
        data['observations'][0].update(country=None,availability='unknown',availability_evidence=None)
        store=Store(self.root/'filters',clock=lambda:self.now)
        store.import_bundle(data)
        html=Path(report(store)['jobs']['path']).read_text()
        self.assertNotIn('data-filter="location"',html)
        self.assertNotIn('data-filter="availability"',html)
        self.assertIn('unknown at capture',html)
        # Do not hide a useful facet just because some rows remain unknown.
        data=bundle('known','known-job')
        data['observations'][0]['country']='DE'
        store.import_bundle(data)
        html=Path(report(store)['jobs']['path']).read_text()
        self.assertIn('data-filter="location"',html)
        self.assertIn('data-filter="availability"',html)
        self.assertIn('data-location="[&quot;DE&quot;]"',html)
        self.assertIn('data-location="[&quot;Unknown&quot;]"',html)

    def test_title_role_families_do_not_classify_evidence(self):
        cases={
            'Senior Machine Learning Engineer': ['Machine learning'],
            'Senior AI Engineer - AI Product': ['AI product engineering'],
            'Member of Technical Staff (Applied AI)': ['Applied AI'],
            'AI/ML Platform Engineer': ['Machine learning','AI infrastructure & MLOps'],
            'LLM Evaluation Engineer': ['LLM & generative AI','AI evaluation & reliability'],
            'AI Agent Engineer': ['Agents & automation'],
            'RAG Engineer': ['Retrieval & knowledge systems'],
            'AI Security Engineer': ['AI security'],
            'Research Scientist (ML)': ['Machine learning','Research & applied science'],
            'Data Engineer': ['Data engineering & pipelines'],
            'AI Engineer': ['General AI engineering'],
            'Insurance Agent': [OTHER],
            'Email Marketing Manager': [OTHER],
            'Principal Product Manager': [OTHER],
            'AI Sales Executive': [OTHER],
        }
        for title, expected in cases.items():
            with self.subTest(title=title):self.assertEqual(role_families(title),expected)
        data=bundle('roles','role-job')
        data['observations'][0]['title']='Senior AI Product Engineer'
        self.store.import_bundle(data)
        before=self.store.snapshot()['snapshot']
        html=Path(report(self.store)['jobs']['path']).read_text()
        self.assertIn('data-filter="role"',html)
        self.assertIn('data-role="[&quot;AI product engineering&quot;]"',html)
        self.assertIn('title-based navigation hints',html)
        self.assertEqual(self.store.snapshot()['snapshot'],before)
        self.assertNotIn('analysis',self.store.status()['counts'])

    def test_source_geography_display_filter_and_no_country_inference(self):
        data=bundle('geography','bg-job')
        row=data['observations'][0]
        row['segments']['source_geography']='Bulgaria'
        self.assertEqual(report_location(row),('Bulgaria','source'))
        self.store.import_bundle(data)
        before=self.store.snapshot()['snapshot']
        html=Path(report(self.store)['jobs']['path']).read_text()
        self.assertIn('data-filter="location"',html)
        self.assertIn('data-location="[&quot;Bulgaria&quot;]"',html)
        self.assertIn('Bulgaria · source location',html)
        self.assertEqual(self.store.snapshot()['snapshot'],before)
        with self.store.transaction() as state:
            self.assertTrue(all(a['payload']['country'] is None for a in state['artifacts'].values()
                                if a['kind']=='observation'))
        for value in ['EMEA','USA, Canada','Anywhere']:
            row['segments']['source_geography']=value
            self.assertEqual(report_location(row),(value,'source'))
        row['country']='BG'
        self.assertEqual(report_location(row),('BG','country'))
        row['country']=None
        for value in [None,'', '   ', []]:
            row['segments']['source_geography']=value
            self.assertEqual(report_location(row),('Unknown','unknown'))
        row['segments']['source_geography']='<img src=x onerror=alert(1)>'
        row['captured_at']='2026-09-08T10:01:01Z'
        row['source_revision']='fixture-hostile-geography'
        data['receipt']['query']='hostile geography fixture'
        self.store.import_bundle(data)
        html=Path(report(self.store)['jobs']['path']).read_text()
        self.assertIn('&lt;img src=x onerror=alert(1)&gt; · source location',html)
        self.assertNotIn('<img ',html)

    def test_hash_only_script_and_escaped_source_no_network(self):
        data=bundle('hostile','req-x');data['observations'][0]['title']='</script><img src=x onerror=alert(1)>'
        self.store.import_bundle(data); result=report(self.store)
        html=Path(result['jobs']['path']).read_text()
        self.assertIn('&lt;/script&gt;&lt;img',html)
        self.assertEqual(html.count('<script>'),1);self.assertNotIn('<img ',html)
        sh=base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
        self.assertIn('sha256-'+sh,html)
        self.assertNotIn('fetch(',SCRIPT);self.assertNotIn('innerHTML',SCRIPT)
        self.assertIn('connect-src &#x27;none&#x27;',html)

    def test_bound_checkout_reports_removed_with_evidence(self):
        self.brief();bind(self.store,self.repo);result=report(self.store)
        target=Path(result['jobs']['path']).parent
        self.assertEqual(target.parent,self.repo/'reports')
        for section in ('jobs','projects'):
            self.assertEqual(Path(result[section]['path']).stat().st_mode & 0o777,0o600)
        self.store.withdraw(self.obs)
        self.assertFalse((target/'jobs.html').exists());self.assertFalse((target/'projects.html').exists())

    def test_expiry_and_legacy_migration_remove_all_views(self):
        self.store=Store(self.root/'expires',clock=lambda:self.now)
        data=bundle();data['policy']['use_until']=(self.now+timedelta(hours=1)).isoformat()
        self.obs=self.store.import_bundle(data)['observations'][0]
        with self.store.transaction() as state:
            self.store.put(state,'offline-report',{'schema_version':1,'created_at':self.now.isoformat(),
                'revision':1,'html':'old'},[self.obs])
        self.assertTrue((self.store.home/'research-report.html').exists())
        bind(self.store,self.repo); result=report(self.store)
        self.assertFalse((self.store.home/'research-report.html').exists())
        self.now+=timedelta(hours=2);self.store.status()
        self.assertFalse(Path(result['jobs']['path']).exists())
        self.assertFalse(Path(result['projects']['path']).exists())

    def test_tracked_and_symlink_destinations_rejected(self):
        (self.repo/'reports').mkdir();(self.repo/'reports'/'leak.txt').write_text('owned')
        subprocess.run(['git','add','-f','reports/leak.txt'],cwd=self.repo,check=True)
        with self.assertRaises(ValueError):bind(self.store,self.repo)
        subprocess.run(['git','rm','--cached','-q','reports/leak.txt'],cwd=self.repo,check=True)
        (self.repo/'reports'/'leak.txt').unlink();(self.repo/'reports').rmdir()
        (self.repo/'reports').symlink_to(self.store.home,target_is_directory=True)
        with self.assertRaises(ValueError):bind(self.store,self.repo)

    def test_missing_location_fails_closed_and_workspaces_do_not_collide(self):
        bind(self.store,self.repo);first=directory(self.store)
        other=Store(self.root/'other',clock=lambda:self.now);bind(other,self.repo)
        self.assertNotEqual(first,directory(other))
        (self.store.home/'report-location.json').unlink()
        with self.assertRaises((ValueError,OSError)):self.store.status()

    def test_failed_second_materialization_cleans_pair(self):
        from tools import research_report_files as files
        original=files.write
        def fail(store,name,html):
            if name=='projects.html':raise OSError('owned failure')
            return original(store,name,html)
        with patch.object(files,'write',side_effect=fail):
            with self.assertRaises(OSError):report(self.store)
        self.assertFalse((self.store.home/'jobs.html').exists())
        self.assertFalse((self.store.home/'projects.html').exists())

    def test_limit_counts_and_absent_projects(self):
        self.store.import_bundle(bundle('second','req-2'))
        result=report(self.store,1)
        self.assertEqual(result['jobs'],{'path':str(self.store.home/'jobs.html'),'shown':1,'total':2})
        self.assertEqual(result['projects']['total'],0)
        self.assertIn('No matching entries',Path(result['projects']['path']).read_text())

    def test_large_report_budget_and_boundary(self):
        for batch in range(2):
            data=bundle('large','req-large-'+str(batch))
            template=data['observations'][0]
            data['observations']=[{**template,'native_id':str(i),
                'url':f'https://example.com/jobs/{i}','employer_requisition':str(i)}
                for i in range(batch*60,(batch+1)*60)]
            data['receipt']['pages'][0]['returned']=60
            self.store.import_bundle(data)
        result=report(self.store,1000)
        self.assertEqual(result['jobs']['shown'],result['jobs']['total'])
        self.assertGreater(result['jobs']['shown'],100)
        with self.assertRaises(ValueError):report(self.store,1001)

    def test_youtube_tab_independent_limit_and_two_files(self):
        self.brief('project',1);self.brief('project',2)
        self.brief('youtube',1);self.brief('youtube',2)
        self.brief('learning');self.brief('product')
        result=report(self.store,1)
        self.assertEqual(result['projects']['shown'],1)
        self.assertEqual(result['projects']['total'],2)
        self.assertEqual(result['youtube']['shown'],1)
        self.assertEqual(result['youtube']['total'],2)
        self.assertEqual(result['projects']['path'],result['youtube']['path'])
        self.assertEqual(result['shown'],2);self.assertEqual(result['overflow'],2)
        html=Path(result['path']).read_text()
        self.assertEqual(html.count('data-kind="project"'),1)
        self.assertEqual(html.count('data-kind="youtube"'),1)
        self.assertIn('YouTube experiments · 2',html)
        self.assertEqual({p.name for p in self.store.home.glob('*.html')},{'jobs.html','projects.html'})

    def test_hidden_youtube_brief_withdrawal_invalidates_report_pair(self):
        self.brief('project');video=self.brief('youtube')
        result=report(self.store)
        self.assertEqual(result['youtube']['total'],1)
        self.store.withdraw(video)
        self.assertFalse(Path(result['jobs']['path']).exists())
        self.assertFalse(Path(result['path']).exists())
        refreshed=report(self.store)
        self.assertEqual(refreshed['projects']['total'],1)
        self.assertEqual(refreshed['youtube']['total'],0)
        self.assertIn('YouTube experiments · 0',Path(refreshed['path']).read_text())

    def test_ui_script_tab_search_reset_and_keyboard(self):
        import shutil
        node=shutil.which('node')
        if not node:self.skipTest('Node unavailable for fixed UI-script behavioral check')
        harness=r'''
const assert = require('node:assert/strict'), vm = require('node:vm'), fs = require('node:fs');
const source = fs.readFileSync(0,'utf8');
const element = (dataset={}) => ({dataset,value:'',hidden:false,textContent:'',events:{},attrs:{},
  options:[{value:''}], addEventListener(n,fn){this.events[n]=fn},
  setAttribute(k,v){this.attrs[k]=v}, getAttribute(k){return this.attrs[k]},
  append(o){this.options.push(o)}, remove(i){this.options.splice(i,1)}, focus(){this.focused=true}});
const cards=[element({kind:'project'}),element({kind:'youtube'})];
cards[0].textContent='Project alpha Hidden beta evidence'; cards[1].textContent='Video beta';
cards.forEach((c,i)=>{c.querySelector=()=>({textContent:i?'Video beta':'Project alpha'})});
cards.forEach((c,i)=>{c.attrs['data-capability']=JSON.stringify([i?'video-only':'project-only'])});
const tabs=[element({tab:'project',total:'1'}),element({tab:'youtube',total:'1'})];
tabs.forEach(t=>{t.id='tab-'+t.dataset.tab});
const filter=element({filter:'capability'});
const ids=Object.fromEntries(['search','search-scope','clear','result-count','no-results','available-count','report-results','brief-tabs'].map(k=>[k,element()]));
const document={querySelectorAll(s){return {'[data-card]':cards,'[data-filter]':[filter],'[data-tab]':tabs}[s]},
 getElementById(k){return ids[k]}, createElement(){return element()}};
vm.runInNewContext(source,{document});
assert.equal(cards[0].hidden,false);assert.equal(cards[1].hidden,true);
assert.equal(filter.options[1].value,'project-only');
// Every input event narrows immediately, without Enter or blur.
for (const value of ['a','al','alph','ALPHA']) {
 ids.search.value=value;ids.search.events.input();assert.equal(cards[0].hidden,false);
}
ids.search.value='beta';ids.search.events.input();assert.equal(cards[0].hidden,true);
ids['search-scope'].value='all';ids['search-scope'].events.change();assert.equal(cards[0].hidden,false);
ids.clear.events.click();assert.equal(ids['search-scope'].value,'titles');
ids.search.value='absent';ids.search.events.input();assert.equal(cards[0].hidden,true);
ids.search.value='';ids.search.events.search();assert.equal(cards[0].hidden,false);

ids.search.value='not-found';ids.search.events.input();assert.equal(ids['no-results'].hidden,false);
tabs[1].events.click();assert.equal(ids.search.value,'');assert.equal(cards[0].hidden,true);assert.equal(cards[1].hidden,false);
assert.equal(filter.options.length,2);assert.equal(filter.options[1].value,'video-only');
assert.equal(ids['result-count'].textContent,'1 of 1 displayed');
ids.search.value='alpha';ids.search.events.input();assert.equal(cards[1].hidden,true);
ids.clear.events.click();assert.equal(cards[1].hidden,false);assert.equal(tabs[1].attrs['aria-selected'],'true');
filter.value='absent';filter.events.change();assert.equal(ids['result-count'].textContent,'0 of 1 displayed');
let prevented=false;tabs[1].events.keydown({key:'ArrowLeft',preventDefault(){prevented=true}});
assert.equal(prevented,true);assert.equal(cards[0].hidden,false);assert.equal(cards[1].hidden,true);
assert.equal(filter.value,'');assert.equal(tabs[0].tabIndex,0);assert.equal(tabs[1].tabIndex,-1);
assert.equal(ids['report-results'].attrs['aria-labelledby'],'tab-project');
// The jobs page has no tabs: input, paste and deletion still update counts.
tabs.length=0;ids.search.value='';ids['search-scope'].value='titles';
vm.runInNewContext(source,{document});
assert.equal(ids['result-count'].textContent,'2 of 2 displayed');
for (const value of ['v','vi','VIDEO','video be']) {
 ids.search.value=value;ids.search.events.input();assert.equal(ids['result-count'].textContent,'1 of 2 displayed');
 assert.equal(cards[0].hidden,true);assert.equal(cards[1].hidden,false);
}
ids.search.value='';ids.search.events.input();assert.equal(ids['result-count'].textContent,'2 of 2 displayed');
// Role families use the same AND filter behavior, including overlapping labels.
filter.dataset.filter='role';
cards[0].attrs['data-role']=JSON.stringify(['Machine learning','AI infrastructure & MLOps']);
cards[1].attrs['data-role']=JSON.stringify(['Applied AI']);
vm.runInNewContext(source,{document});
filter.value='Machine learning';filter.events.change();
assert.equal(cards[0].hidden,false);assert.equal(cards[1].hidden,true);
ids.search.value='video';ids.search.events.input();assert.equal(ids['result-count'].textContent,'0 of 2 displayed');
ids.search.value='';ids.search.events.input();filter.value='AI infrastructure & MLOps';filter.events.change();
assert.equal(cards[0].hidden,false);assert.equal(cards[1].hidden,true);
ids.clear.events.click();assert.equal(filter.value,'');assert.equal(ids['result-count'].textContent,'2 of 2 displayed');
console.log('Title/full-content typeahead, tab, filter, clear and keyboard behavior passed.');
'''
        result=subprocess.run([node,'-e',harness],input=SCRIPT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
