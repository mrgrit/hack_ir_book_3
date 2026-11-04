"""Load one verified book3 dataset into a NEW index; never alter existing indexes."""
import argparse,base64,getpass,json,re,ssl,urllib.request,urllib.error
from pathlib import Path
from check_dataset import check

def index_name(manifest):
    name=manifest['index']
    if not re.fullmatch(r'book3-r(?:0[1-9]|10|12|13|15)-[a-z0-9][a-z0-9-]{0,39}',name):
        raise ValueError('Expected an exact book3 round index, without wildcards')
    return name

def upload(folder,call,batch_size=1000):
    check(folder)
    m=json.loads((folder/'manifest.json').read_text(encoding='utf8'));name=index_name(m)
    status,_=call('HEAD','/'+name)
    if status!=404:raise ValueError('Target must be absent (HTTP 404); stop and inspect the existing index')
    template=json.loads((folder/'template.json').read_text(encoding='utf8'))
    if template['index_patterns']!=[name]:raise ValueError('Template target differs from manifest')
    definition=template['template']
    definition['mappings']['_meta']={'book3':{'bulk_sha256':m['files']['events.bulk.ndjson'],'round':m['round'],'expected_events':m['total']}}
    status,response=call('PUT','/'+name,definition)
    if status!=200 or not response.get('acknowledged'):raise ValueError('Index creation failed: '+str(response))
    created=0
    def send(lines):
        status,result=call('POST','/_bulk',''.join(lines),'application/x-ndjson')
        items=result.get('items',[])
        if status!=200 or result.get('errors') or len(items)!=len(lines)//2 or any(x.get('create',{}).get('status')!=201 for x in items):
            raise RuntimeError('Bulk failed; retain the partial index for inspection; no automatic retry or deletion')
        return len(items)
    with (folder/'events.bulk.ndjson').open(encoding='utf8') as f:
        lines=[]
        for action in f:
            lines.extend([action,f.readline()])
            if len(lines)==batch_size*2:created+=send(lines);lines=[]
        if lines:created+=send(lines)
    status,r=call('POST','/'+name+'/_refresh')
    if status!=200 or r.get('_shards',{}).get('failed',0):raise RuntimeError('Refresh failed')
    status,r=call('GET','/'+name+'/_count')
    if status!=200 or r.get('count')!=m['total'] or created!=m['total']:raise RuntimeError('Final count mismatch')
    return {'status':'pass','index':name,'created':created,'count':r['count'],'bulk_sha256':m['files']['events.bulk.ndjson'],'existing_indexes_modified':False,'global_templates_modified':False}

def client(url,user,password,cafile=None,insecure=False):
    if not url.startswith('https://'):raise ValueError('Use an HTTPS indexer URL')
    context=ssl._create_unverified_context() if insecure else ssl.create_default_context(cafile=cafile)
    auth='Basic '+base64.b64encode((user+':'+password).encode()).decode()
    def call(method,path,body=None,ctype='application/json'):
        data=None if body is None else (body if isinstance(body,str) else json.dumps(body)).encode()
        request=urllib.request.Request(url.rstrip('/')+path,data=data,method=method,headers={'Authorization':auth,'Content-Type':ctype})
        try:
            with urllib.request.urlopen(request,context=context,timeout=120) as r:
                raw=r.read();return r.status,json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw=e.read()
            try:result=json.loads(raw) if raw else {}
            except ValueError:result={'message':raw.decode(errors='replace')[:500]}
            return e.code,result
    return call

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('folder',type=Path);ap.add_argument('--url',required=True);ap.add_argument('--user',default='admin')
    tls=ap.add_mutually_exclusive_group();tls.add_argument('--ca-cert');tls.add_argument('--insecure',action='store_true',help='Only for the isolated kt66 self-signed demonstration environment')
    args=ap.parse_args();password=getpass.getpass('Indexer password: ')
    result=upload(args.folder,client(args.url,args.user,password,args.ca_cert,args.insecure))
    print(json.dumps(result,ensure_ascii=False,indent=2))
