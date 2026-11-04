"""Prepare and load a NEW observation index; never execute or transmit captured traffic."""
import argparse,getpass,hashlib,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from load_dataset import client

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def mapping():
    def fields(names,kind):return {n:{'type':kind} for n in names.split()}
    data={**fields('timestamp event_type flow_id proto app_proto','keyword'),**fields('src_ip dest_ip','ip'),**fields('src_port dest_port pcap_cnt tx_id','long')}
    for obj,props in {
      'http':{**fields('hostname url http_method protocol','keyword'),**fields('status length','long')},
      'dns':fields('type rrname rrtype rcode','keyword'),
      'tls':fields('sni version','keyword'),
      'alert':{**fields('signature action','keyword'),**fields('signature_id severity','long')},
      'flow':{**fields('start end state reason','keyword'),**fields('age bytes_toserver bytes_toclient pkts_toserver pkts_toclient','long')}
    }.items():data[obj]={'properties':props}
    provenance={'synthetic':{'type':'boolean'},**fields('run_id pcap_sha256 eve_sha256 source_kind sensor_version','keyword'),'source_line':{'type':'long'}}
    props={'timestamp':{'type':'date'},'data':{'properties':data},'book3':{'properties':provenance}}
    return {'settings':{'number_of_shards':1,'number_of_replicas':0},'mappings':{'dynamic':False,'properties':props}}
def prepare(a):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,39}',a.run_id):raise ValueError('Invalid run id')
    if a.out.exists():raise FileExistsError(a.out)
    meta=json.loads(a.pcap_info.read_text('utf8'));ph=meta['sha256']
    if not re.fullmatch('[0-9a-f]{64}',ph) or meta['packets']<=0:raise ValueError('Invalid PCAP metadata')
    eh=sha(a.eve);index='book3-pcap-'+a.run_id;docs=[];all_kinds=Counter();selected=Counter()
    for line,raw in enumerate(a.eve.read_text(encoding='utf8').splitlines(),1):
        d=json.loads(raw);kind=d['event_type'];all_kinds[kind]+=1
        if kind not in {'flow','dns','http','tls','alert'}:continue
        t=datetime.fromisoformat(d['timestamp'])
        if t.tzinfo is None:raise ValueError('Timestamp must include timezone')
        if 'flow_id' in d:d['flow_id']=str(d['flow_id'])
        selected[kind]+=1
        doc={'timestamp':t.astimezone(timezone.utc).isoformat(timespec='milliseconds'),'data':d,'book3':{'synthetic':False,'source_kind':'pcap-observation','run_id':a.run_id,'pcap_sha256':ph,'eve_sha256':eh,'source_line':line,'sensor_version':a.sensor_version}}
        docs.append((t,line,doc))
    if not docs:raise ValueError('No selected observations')
    docs.sort(key=lambda x:(x[0],x[1]));a.out.mkdir(parents=True)
    with (a.out/'events.bulk.ndjson').open('w',encoding='utf8',newline='\n') as f:
        for _,line,d in docs:
            f.write(json.dumps({'create':{'_index':index,'_id':f'{eh[:16]}-{line:07d}'}})+'\n'+json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    put(a.out/'definition.json',mapping())
    m={'schema_version':1,'source_kind':'pcap-observation','index':index,'total':len(docs),'selected_counts':dict(selected),'all_eve_counts':dict(all_kinds),'pcap':meta,'eve_sha256':eh,'sensor_version':a.sensor_version,'config_sha256':sha(a.config),'rules_sha256':sha(a.rules),'timestamp_transform':'UTC millisecond search field; original EVE timestamp retained in data.timestamp','flow_id_transform':'decimal string to preserve identity across JSON clients','manager_alerts_created':False,'files':{n:sha(a.out/n) for n in ['events.bulk.ndjson','definition.json']}}
    put(a.out/'manifest.json',m);return m
def check(folder):
    m=json.loads((folder/'manifest.json').read_text('utf8'));name=m['index']
    if not re.fullmatch(r'book3-pcap-[a-z0-9][a-z0-9-]{0,39}',name):raise ValueError('Exact PCAP index required')
    for n,h in m['files'].items():
        if n not in ['events.bulk.ndjson','definition.json'] or sha(folder/n)!=h:raise ValueError('File hash mismatch')
    ids=set();counts=Counter();prev=''
    with (folder/'events.bulk.ndjson').open(encoding='utf8') as f:
        for line in f:
            action=json.loads(line)['create'];d=json.loads(f.readline())
            assert action['_index']==name and action['_id'] not in ids
            assert d['book3']['synthetic'] is False and d['book3']['pcap_sha256']==m['pcap']['sha256'] and d['book3']['eve_sha256']==m['eve_sha256']
            assert prev<=d['timestamp'];prev=d['timestamp'];ids.add(action['_id']);counts[d['data']['event_type']]+=1
    assert len(ids)==m['total'] and dict(counts)==m['selected_counts']
    return m
def upload(folder,call):
    m=check(folder);index=m['index'];status,_=call('HEAD','/'+index)
    if status!=404:raise ValueError('Target already exists or cannot be inspected; no overwrite')
    definition=json.loads((folder/'definition.json').read_text('utf8'))
    definition['mappings']['_meta']={'book3':{k:m[k] for k in ['source_kind','eve_sha256','total']}|{'pcap_sha256':m['pcap']['sha256'],'bulk_sha256':m['files']['events.bulk.ndjson']}}
    status,r=call('PUT','/'+index,definition)
    if status!=200 or not r.get('acknowledged'):raise RuntimeError(r)
    lines=(folder/'events.bulk.ndjson').read_text('utf8').splitlines(keepends=True)
    for i in range(0,len(lines),2000):
        chunk=lines[i:i+2000];status,r=call('POST','/_bulk',''.join(chunk),'application/x-ndjson')
        if status!=200 or r.get('errors') or len(r.get('items',[]))!=len(chunk)//2 or any(x.get('create',{}).get('status')!=201 for x in r['items']):raise RuntimeError('Partial load retained; inspect without retry/delete')
    status,r=call('POST','/'+index+'/_refresh')
    if status!=200 or r.get('_shards',{}).get('failed'):raise RuntimeError(r)
    status,r=call('GET','/'+index+'/_count')
    if status!=200 or r.get('count')!=m['total']:raise RuntimeError(r)
    return {'status':'pass','index':index,'count':r['count'],'manager_alerts_created':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('prepare')
    for name in ['eve','pcap-info','config','rules','out']:a.add_argument('--'+name,type=Path,required=True)
    a.add_argument('--run-id',required=True);a.add_argument('--sensor-version',required=True)
    a=sub.add_parser('check');a.add_argument('folder',type=Path)
    a=sub.add_parser('load');a.add_argument('folder',type=Path);a.add_argument('--url',required=True);a.add_argument('--user',default='admin');tls=a.add_mutually_exclusive_group();tls.add_argument('--ca-cert');tls.add_argument('--insecure',action='store_true')
    a=sub.add_parser('select');a.add_argument('eve',type=Path);a.add_argument('--kind',required=True)
    a=p.parse_args()
    if a.command=='select':
        for raw in a.eve.read_text(encoding='utf8').splitlines():
            if json.loads(raw)['event_type']==a.kind:print(raw.rstrip());break
        else:raise ValueError('No event of requested kind')
    else:
        result=prepare(a) if a.command=='prepare' else check(a.folder) if a.command=='check' else upload(a.folder,client(a.url,a.user,getpass.getpass('Indexer password: '),a.ca_cert,a.insecure))
        print(json.dumps(result,ensure_ascii=False,indent=2))
