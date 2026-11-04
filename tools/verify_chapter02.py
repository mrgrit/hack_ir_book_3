"""Cross-check saved live query responses against original synthetic events."""
import argparse,json,sys
from collections import Counter,defaultdict
from pathlib import Path
from check_dataset import check,parse_time
from prepare_round import sha

def verify(folder,responses):
    checked=check(folder);r=json.loads(responses.read_text('utf8'));docs=[]
    with (folder/'events.bulk.ndjson').open(encoding='utf8') as f:
        for action in f:docs.append(json.loads(f.readline()))
    assert len(r)==14 and not any('error' in v or v.get('timed_out') or v.get('_shards',{}).get('failed',0) for v in r.values())
    assert len(docs)==r['01']['hits']['total']['value']==85306
    assert r['01']['hits']['total']['relation']=='eq'
    for key,doc in [('first',docs[0]),('last',docs[-1])]:
        assert round(parse_time(doc['timestamp']).timestamp()*1000)==r['01']['aggregations'][key]['value']
    for field,kind in [('timestamp','date'),('agent.name','keyword'),('data.bytes','long'),('data.srcip','keyword'),('data.src_ip','keyword')]:
        assert r['02']['fields'][field][kind]['aggregatable'] is True
    agents=Counter(d['agent']['name'] for d in docs)
    assert agents=={b['key']:b['doc_count'] for b in r['03']['aggregations']['by_agent']['buckets']}
    webs=[d for d in docs if d['decoder']['name']=='web-accesslog'];vhosts=defaultdict(list)
    for d in webs:vhosts[d['data']['vhost']].append(d['data'])
    cardinality=[]
    for b in r['04']['aggregations']['by_vhost']['buckets']:
        ds=vhosts[b['key']];count=len(ds);exact=len({d['srcip'] for d in ds});total=sum(d['bytes'] for d in ds)
        assert count==b['doc_count'] and total==b['bytes']['value']
        assert abs(total/count-b['avg_bytes']['value'])<1e-6
        assert exact==b['visitors']['value']
        cardinality.append({'vhost':b['key'],'exact_distinct_ips':exact,'estimated_distinct_ips':b['visitors']['value']})
    statuses=Counter(d['data']['id'] for d in webs)
    for key,status in [('ok','200'),('forbidden','403'),('not_found','404')]:
        assert statuses[status]==r['05']['aggregations']['by_status']['buckets'][key]['doc_count']
        assert len({d['data']['srcip'] for d in webs if d['data']['id']==status})==r['05']['aggregations']['by_status']['buckets'][key]['visitors']['value']
    assert sum(b['doc_count'] for b in r['06']['aggregations']['per_week']['buckets'])==len(docs)
    server=[d for d in docs if d.get('data',{}).get('src_ip','').startswith('10.20.40.')]
    destinations=[]
    for b in r['07']['aggregations']['by_dst']['buckets']:
        ds=[d for d in server if d['data'].get('dest_ip')==b['key']]
        days=Counter(parse_time(d['timestamp']).date().isoformat() for d in ds)
        srcs=sorted({d['data']['src_ip'] for d in ds})
        assert len(ds)==b['doc_count'] and len(srcs)==b['srcs']['value'] and len(days)==len(b['active_days']['buckets'])
        destinations.append({'destination':b['key'],'count':len(ds),'sources':srcs,'active_days':len(days)})
    candidate=[d for d in server if d['data'].get('dest_ip')=='53.81.8.74']
    days=Counter(parse_time(d['timestamp']).date().isoformat() for d in candidate)
    assert days=={b['key_as_string']:b['doc_count'] for b in r['08']['aggregations']['per_day']['buckets']}
    assert max(days,key=days.get)=='2026-10-30' and max(days.values())==503
    paths=Counter((d['data']['http']['url'],d['data']['http']['http_method'],d['data']['http']['http_user_agent']) for d in candidate)
    assert paths==Counter({('/beat','POST','Go-http-client/1.1'):2261,('/file/download','POST','curl/7.81.0'):1})
    observed_paths=Counter({(u['key'],m['key'],a['key']):a['doc_count'] for u in r['09']['aggregations']['by_url']['buckets'] for m in u['method']['buckets'] for a in m['ua']['buckets']})
    assert paths==observed_paths
    gap_results={}
    for key in ('10','13'):
        hits=r[key]['hits'];ts=[parse_time(x['_source']['timestamp']) for x in hits['hits']]
        assert len(ts)==8 and ts==sorted(ts)
        start,end=('2026-10-30T10:30:00+09:00','2026-10-30T10:40:00+09:00') if key=='10' else ('2026-10-29T00:00:00+09:00','2026-10-30T00:00:00+09:00')
        matching=[d for d in candidate if d['data']['src_ip']=='10.20.40.81' and d['data']['http']['url']=='/beat' and parse_time(start)<=parse_time(d['timestamp'])<parse_time(end)]
        assert hits['total']=={'value':len(matching),'relation':'eq'}
        assert ts==[parse_time(d['timestamp']) for d in matching[:8]]
        gap_results[key]={'total_hits':hits['total'],'sample_size':len(ts),'timestamps':[t.isoformat() for t in ts],'gaps_seconds':[round((b-a).total_seconds(),3) for a,b in zip(ts,ts[1:])],'sample_event_ids':[h['_id'] for h in hits['hits']]}
    assert gap_results['10']['gaps_seconds'][:3]==[32.212,39.582,36.993]
    assert gap_results['13']['gaps_seconds'][:3]==[3711.48,4569.31,2923.668]
    assert [b['key'] for b in r['11']['aggregations']['by_dst']['buckets']]==['53.81.8.74']
    rules=Counter(d['rule']['description'] for d in docs if d.get('rule',{}).get('level',0)>=7)
    assert rules=={b['key']:b['doc_count'] for b in r['12']['aggregations']['by_rule']['buckets']}
    m=json.loads((folder/'manifest.json').read_text('utf8'));assert r['14'][m['index']]['mappings']['_meta']['book3']['bulk_sha256']==m['files']['events.bulk.ndjson']
    return {'status':'pass','checked_dataset':checked,'index':m['index'],'bulk_sha256':m['files']['events.bulk.ndjson'],'live_query_count':len(r),'agent_counts':dict(agents),'web_access_count':len(webs),'web_status_counts':dict(statuses),'cardinality_crosscheck':cardinality,'destination_crosscheck':destinations,'timestamp_samples':gap_results,'generated_rule_counts':dict(rules),'response_sha256':sha(responses),'network_operations_in_this_verifier':0}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('folder',type=Path);ap.add_argument('responses',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    result=verify(a.folder,a.responses);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(result['status'],result['live_query_count'],'queries',result['web_access_count'],'web events')
