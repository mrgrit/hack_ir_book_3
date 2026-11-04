"""Compare saved R02 live responses with every original synthetic event."""
import argparse,json
from collections import Counter
from pathlib import Path
from check_dataset import check,parse_time
from prepare_round import sha
def verify(folder,responses):
    checked=check(folder);r=json.loads(responses.read_text('utf8'));docs=[]
    with (folder/'events.bulk.ndjson').open(encoding='utf8') as f:
        for action in f:docs.append(json.loads(f.readline()))
    assert len(r)==9 and all(not x.get('timed_out') and not x.get('_shards',{}).get('failed',0) and 'error' not in x for x in r.values())
    assert r['01']['hits']['total']=={'value':len(docs),'relation':'eq'}
    assert Counter(d['decoder']['name'] for d in docs)=={b['key']:b['doc_count'] for b in r['01']['aggregations']['sources']['buckets']}
    web=[d for d in docs if d['decoder']['name']=='web-accesslog'];nf=[d for d in web if d['data']['id']=='404']
    for b in r['02']['aggregations']['by_ip']['buckets']:
        ds=[d for d in web if d['data']['srcip']==b['key']];assert len(ds)==b['doc_count']
        ua=b['ua']['buckets'][0];assert sum(d['data']['user_agent']==ua['key'] for d in ds)==ua['doc_count']
    for b in r['03']['aggregations']['by_ip']['buckets']:
        ds=[d for d in nf if d['data']['srcip']==b['key']]
        assert len(ds)==b['doc_count'] and len({d['data']['url'] for d in ds})==b['urls']['value'] and len({d['data']['vhost'] for d in ds})==b['hosts']['value']
    apis=[d for d in nf if d['data']['vhost']=='neobank.kt66.lab' and d['data']['url'].startswith('/api/')]
    for b in r['04']['aggregations']['by_url']['buckets']:
        ds=[d for d in apis if d['data']['url']==b['key']]
        assert len(ds)==b['doc_count'] and len({d['data']['srcip'] for d in ds})==b['ips']['value']
    fw=[d for d in docs if d['decoder']['name']=='kt66-nft'];assert all(d['data']['action']=='DROP' for d in fw)
    for b in r['05']['aggregations']['by_ip']['buckets']:
        ds=[d for d in fw if d['data']['srcip']==b['key']]
        assert len(ds)==b['doc_count'] and len({d['data']['dstport'] for d in ds})==b['ports']['value']
        assert len({d['data']['dstip'] for d in ds})==b['destinations']['value']
        assert len({parse_time(d['timestamp']).date() for d in ds})==len(b['days']['buckets'])
    candidate=[d for d in web if d['data']['srcip']=='221.49.17.120']
    for b in r['06']['aggregations']['days']['buckets']:
        ds=[d for d in candidate if d['timestamp'][:10]==b['key_as_string']]
        assert len(ds)==b['doc_count'] and Counter(d['data']['id'] for d in ds)=={s['key']:s['doc_count'] for s in b['status']['buckets']}
    for n,ds in [('07',[d for d in fw if d['data']['srcip']=='142.66.143.170']),('08',candidate)]:
        assert r[n]['hits']['total']=={'value':len(ds),'relation':'eq'}
        assert [h['_source']['timestamp'] for h in r[n]['hits']['hits']]==[d['timestamp'] for d in ds[:6]]
    hidden=[d for d in apis if d['data']['url'] in ['/api/v1/admin/users','/api/v1/accounts/export?format=csv']]
    assert len(hidden)==r['09']['hits']['total']['value']==444
    assert len({d['data']['srcip'] for d in hidden})==r['09']['aggregations']['sources']['value']==300
    counts=Counter(d['data']['srcip'] for d in hidden);assert max(counts.values())==2 and min(counts.values())==1
    return {'status':'pass','dataset_check':checked,'queries_checked':9,'response_sha256':sha(responses),'bulk_sha256':sha(folder/'events.bulk.ndjson'),'web':len(web),'firewall':len(fw),'web_candidate':{'all':len(candidate),'404':sum(d['data']['id']=='404' for d in candidate),'active_days':len({d['timestamp'][:10] for d in candidate})},'distributed':{'requests':len(hidden),'sources':len(counts),'both_paths':sum(n==2 for n in counts.values())},'network_operations':0}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('responses',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    r=verify(a.folder,a.responses);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print('PASS',r['queries_checked'],'queries',r['distributed'])
