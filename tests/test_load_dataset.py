"""Loader guardrails with a real validated two-event fixture; no server needed."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from load_dataset import upload,index_name
from check_dataset import parse_time

class LoaderTests(unittest.TestCase):
    def fixture(self,folder):
        bulk='';truth=''
        for n in range(2):
            bulk+=json.dumps({'create':{'_index':'book3-r01-test','_id':str(n)}})+'\n'
            bulk+=json.dumps({'timestamp':f'2026-08-03T00:00:0{n}+0900','book3':{'synthetic':True}})+'\n'
            truth+=json.dumps({'event_id':str(n),'origin':'background'})+'\n'
        values={'events.bulk.ndjson':bulk,'truth.jsonl':truth,'template.json':json.dumps({'index_patterns':['book3-r01-test'],'template':{'settings':{},'mappings':{}}})}
        for k,v in values.items():(folder/k).write_text(v,encoding='utf8')
        manifest={'index':'book3-r01-test','round':'r01','total':2,'counts':{'background':2},'start_inclusive':'2026-08-03T00:00:00+0900','end_exclusive':'2026-08-04T00:00:00+0900','files':{k:hashlib.sha256((folder/k).read_bytes()).hexdigest() for k in values}}
        (folder/'manifest.json').write_text(json.dumps(manifest),encoding='utf8')

    def test_python310_offset_normalization(self):
        self.assertEqual(parse_time('2026-08-03T00:00:00+0900'),parse_time('2026-08-03T00:00:00+09:00'))

    def test_exact_namespace(self):
        for name in ['wazuh-alerts-*','book3-*','book3-r01-test/_delete_by_query','book3-r11-test']:
            with self.assertRaises(ValueError):index_name({'index':name})

    def test_existing_or_unauthorized_index_stops_without_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);self.fixture(folder)
            for status in (200,401,403,500):
                calls=[]
                def call(*args):calls.append(args);return status,{}
                with self.assertRaises(ValueError):upload(folder,call)
                self.assertEqual(calls,[('HEAD','/book3-r01-test')])

    def test_corrupt_file_stops_before_network(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);self.fixture(folder)
            with (folder/'events.bulk.ndjson').open('a') as f:f.write('{}\n')
            with self.assertRaises(ValueError):upload(folder,lambda *a:self.fail('network called'))

    def test_bulk_item_error_stops_without_retry_or_delete(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);self.fixture(folder);calls=[]
            def call(method,path,*body):
                calls.append((method,path))
                if method=='HEAD':return 404,{}
                if method=='PUT':return 200,{'acknowledged':True}
                return 200,{'errors':True,'items':[{'create':{'status':409}}]}
            with self.assertRaises(RuntimeError):upload(folder,call,batch_size=1)
            self.assertEqual(calls,[('HEAD','/book3-r01-test'),('PUT','/book3-r01-test'),('POST','/_bulk')])

    def test_create_batches_and_final_count(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);self.fixture(folder);batches=[]
            def call(method,path,body=None,*extra):
                if method=='HEAD':return 404,{}
                if method=='PUT':
                    self.assertEqual(body['mappings']['_meta']['book3']['expected_events'],2)
                    return 200,{'acknowledged':True}
                if path=='/_bulk':
                    self.assertTrue(body.endswith('\n'));batches.append(body)
                    self.assertEqual(json.loads(body.splitlines()[0])['create']['_index'],'book3-r01-test')
                    return 200,{'errors':False,'items':[{'create':{'status':201}}]}
                if path.endswith('_refresh'):return 200,{'_shards':{'failed':0}}
                if path.endswith('_count'):return 200,{'count':2}
                self.fail(path)
            self.assertEqual(upload(folder,call,batch_size=1)['created'],2)
            self.assertEqual(len(batches),2)

if __name__=='__main__':unittest.main()
