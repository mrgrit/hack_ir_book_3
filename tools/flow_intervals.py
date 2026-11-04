"""Read synthetic bulk files locally; report gaps for one directed flow tuple."""
import argparse,json,statistics
from datetime import datetime
from pathlib import Path
def summarize(folder,src,dst,port):
    rows=[]
    with (Path(folder)/'events.bulk.ndjson').open(encoding='utf8') as f:
        while True:
            action=f.readline()
            if not action:break
            event=json.loads(f.readline());d=event.get('data',{})
            if d.get('event_type')=='flow' and (d.get('src_ip'),d.get('dest_ip'),str(d.get('dest_port')))==(src,dst,str(port)):
                rows.append(event)
    rows.sort(key=lambda x:datetime.fromisoformat(x['timestamp']))
    gaps=[round((datetime.fromisoformat(b['timestamp'])-datetime.fromisoformat(a['timestamp'])).total_seconds(),3) for a,b in zip(rows,rows[1:])]
    return {'events':len(rows),'intervals':len(gaps),'first':rows[0]['timestamp'] if rows else None,'last':rows[-1]['timestamp'] if rows else None,'minimum_seconds':min(gaps) if gaps else None,'median_seconds':statistics.median(gaps) if gaps else None,'maximum_seconds':max(gaps) if gaps else None,'maximum_gap_endpoints':next(([a['timestamp'],b['timestamp']] for a,b,g in zip(rows,rows[1:],gaps) if g==max(gaps)),None) if gaps else None,'interpretation':'Observed event gaps; not packet capture, process attribution, or proof of C2.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--src',required=True);p.add_argument('--dst',required=True);p.add_argument('--port',required=True);a=p.parse_args();print(json.dumps(summarize(a.folder,a.src,a.dst,a.port),ensure_ascii=False,indent=2))
