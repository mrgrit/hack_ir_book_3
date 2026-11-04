"""Compare sensor observations and calculate gaps between matching Zeek HTTP requests."""
import argparse,hashlib,json,statistics
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
def rows(p):return [json.loads(x) for x in p.read_text(encoding='utf8').splitlines()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def report(a):
 e=rows(a.eve);h=rows(a.http);c=rows(a.conn)
 s=[x for x in e if x['event_type']=='http' and x['src_ip']==a.source and x['http'].get('hostname')==a.host and x['http'].get('url')==a.uri]
 z=sorted([x for x in h if x['id.orig_h']==a.source and x.get('host')==a.host and x.get('uri')==a.uri],key=lambda x:x['ts'])
 if len(z)<2:raise ValueError('At least two matching HTTP requests required')
 gaps=[y['ts']-x['ts'] for x,y in zip(z,z[1:])];uids={x['uid'] for x in z};joined=[x for x in c if x['uid'] in uids]
 assert uids=={x['uid'] for x in joined},'HTTP uid without conn record'
 result={'filter':{'source':a.source,'host':a.host,'uri':a.uri},'files':{p.name:sha(p) for p in [a.eve,a.http,a.conn]},'suricata_counts':dict(Counter(x['event_type'] for x in e)),'zeek_counts':{'http':len(h),'conn':len(c)},'repeat':{'suricata':len(s),'suricata_status':dict(Counter(str(x['http'].get('status','missing')) for x in s)),'zeek':len(z),'zeek_status':dict(Counter(str(x.get('status_code','missing')) for x in z)),'zeek_connection_count':len(uids),'first_request_utc':datetime.fromtimestamp(z[0]['ts'],timezone.utc).isoformat(),'last_request_utc':datetime.fromtimestamp(z[-1]['ts'],timezone.utc).isoformat(),'gaps':{'n':len(gaps),'unit':'seconds','min':min(gaps),'median':statistics.median(gaps),'p95':statistics.quantiles(gaps,n=100,method='inclusive')[94],'max':max(gaps),'method':'chronological adjacent requests; includes connection transitions; linear inclusive quantile'}}}
 if a.deeper:
  d=rows(a.deeper);r=[x for x in d if x['event_type']=='http' and x['src_ip']==a.source and x['http'].get('hostname')==a.host and x['http'].get('url')==a.uri]
  result['deeper']={'sha256':sha(a.deeper),'repeat':len(r),'status':dict(Counter(str(x['http'].get('status','missing')) for x in r))}
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['eve','http','conn']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--deeper',type=Path)
 for n in ['source','host','uri']:p.add_argument('--'+n,required=True)
 print(json.dumps(report(p.parse_args()),ensure_ascii=False,indent=2))
