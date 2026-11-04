"""Reconcile saved read-only queries against source events, without SIEM access.

This deliberately small exact evaluator rejects unsupported clauses. It checks
returned counts/metrics/source documents, not analyst intent or omitted candidates.
"""
import argparse,fnmatch,json,math
from collections import Counter
from pathlib import Path
from check_dataset import check,parse_time
from prepare_round import sha
ROOT=Path(__file__).resolve().parents[1]
def field(d,key):
    v=d
    for part in key.split('.'):
        if not isinstance(v,dict):return None
        v=v.get(part)
    return v
def matches(d,q):
    if 'match_all' in q:return True
    if 'bool' in q:
        b=q['bool'];must=b.get('filter',[])+b.get('must',[]);should=b.get('should',[])
        required=b.get('minimum_should_match',0 if must else (1 if should else 0))
        return all(matches(d,x) for x in must) and not any(matches(d,x) for x in b.get('must_not',[])) and sum(matches(d,x) for x in should)>=required
    op,arg=next(iter(q.items()))
    if op=='exists':return field(d,arg['field']) is not None
    k,v=next(iter(arg.items()));actual=field(d,k)
    if actual is None:return False
    if op=='term':return actual==v
    if op=='terms':return actual in v
    if op=='prefix':return str(actual).startswith(v)
    if op=='wildcard':return fnmatch.fnmatchcase(str(actual),v)
    if op=='range':
        for test,limit in v.items():
            a,c=(parse_time(actual).timestamp(),parse_time(limit).timestamp()) if k=='timestamp' else (actual,limit)
            if not {'gte':a>=c,'gt':a>c,'lte':a<=c,'lt':a<c}[test]:return False
        return True
    raise ValueError('Unsupported query '+op)
def compare_aggs(docs,definitions,actual):
    for name,definition in definitions.items():
        result=actual[name];op=next(k for k in definition if k!='aggs');arg=definition[op]
        if op=='terms':
            counts=Counter(field(d,arg['field']) for d in docs if field(d,arg['field']) is not None)
            returned=0
            for b in result['buckets']:
                subset=[d for d in docs if field(d,arg['field'])==b['key']]
                assert b['doc_count']==counts[b['key']],(name,b['key'])
                returned+=len(subset);compare_aggs(subset,definition.get('aggs',{}),b)
            assert result['sum_other_doc_count']==sum(counts.values())-returned,name
        elif op in ('filter','filters'):
            filters={'_':arg} if op=='filter' else arg['filters']
            for key,query in filters.items():
                subset=[d for d in docs if matches(d,query)];b=result if op=='filter' else result['buckets'][key]
                assert b['doc_count']==len(subset),(name,key)
                compare_aggs(subset,definition.get('aggs',{}),b)
        elif op=='date_histogram':
            covered=0
            for b in result['buckets']:
                lower=b['key']/1000
                if 'fixed_interval' in arg:
                    interval=arg['fixed_interval'];seconds=int(interval[:-1])*{'s':1,'m':60,'h':3600,'d':86400}[interval[-1]]
                else:seconds={'day':86400,'1d':86400,'week':604800,'1w':604800}[arg['calendar_interval']]
                subset=[d for d in docs if lower<=parse_time(field(d,arg['field'])).timestamp()<lower+seconds]
                assert len(subset)==b['doc_count'],(name,b['key_as_string']);covered+=len(subset)
                compare_aggs(subset,definition.get('aggs',{}),b)
            assert covered==len(docs),name
        elif op in ('min','max','sum','avg','cardinality','value_count'):
            values=[field(d,arg['field']) for d in docs if field(d,arg['field']) is not None]
            if arg['field']=='timestamp':values=[parse_time(x).timestamp()*1000 for x in values]
            if op=='cardinality':expected=len(set(values))
            elif op=='value_count':expected=len(values)
            elif not values:expected=0 if op=='sum' else None
            else:expected={'min':min,'max':max,'sum':sum,'avg':lambda a:sum(a)/len(a)}[op](values)
            assert (result['value'] is None if expected is None else math.isclose(result['value'],expected,rel_tol=1e-9,abs_tol=0.001)),(name,result['value'],expected)
        else:raise ValueError('Unsupported aggregation '+op)
def verify(chapter,folders):
    datasets={};checks=[]
    for folder in folders:
        checks.append({'folder':folder.name,**check(folder),'bulk_sha256':sha(folder/'events.bulk.ndjson')})
        index=json.loads((folder/'manifest.json').read_text('utf8'))['index'];docs=[]
        with (folder/'events.bulk.ndjson').open(encoding='utf8') as f:
            for line in f:
                action=json.loads(line)['create'];d=json.loads(f.readline());d['_id']=action['_id'];docs.append(d)
        datasets[index]=docs
    queries=json.loads((ROOT/f'examples/chapter{chapter:02}/queries.json').read_text('utf8'))
    responses_path=ROOT/f'editorial/chapter{chapter:02}-query-results.json';responses=json.loads(responses_path.read_text('utf8'));totals={}
    for n,query in queries.items():
        body=query['body'];index=query['path'].split('/')[1];r=responses[n]
        assert not r.get('timed_out') and not r.get('_shards',{}).get('failed',0) and 'error' not in r
        docs=[d for d in datasets[index] if matches(d,body['query'])];totals[n]=len(docs)
        assert r['hits']['total']=={'value':len(docs),'relation':'eq'},(n,r['hits']['total'],len(docs))
        compare_aggs(docs,body.get('aggs',{}),r.get('aggregations',{}))
        if body.get('size',10):
            for sort in reversed(body.get('sort',[])):
                k,direction=next(iter(sort.items()));docs.sort(key=lambda d:field(d,k),reverse=direction=='desc')
            expected=docs[:body.get('size',10)];hits=r['hits']['hits']
            assert [d['_id'] for d in expected]==[h['_id'] for h in hits],n
            for d,h in zip(expected,hits):
                for k in body.get('_source',[]):assert field(d,k)==field(h['_source'],k),(n,k)
    result={'status':'pass','chapter':chapter,'queries_checked':len(queries),'matched_documents':totals,'datasets':checks,'response_sha256':sha(responses_path),'network_operations':0,'scope':'Exact source counts, returned buckets and metrics, selected hit IDs and fields; query intent and unreturned candidates require editorial review.'}
    (ROOT/f'editorial/chapter{chapter:02}-data-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print('PASS',len(queries),'queries',totals)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('chapter',type=int);p.add_argument('folders',type=Path,nargs='+');a=p.parse_args();verify(a.chapter,a.folders)
