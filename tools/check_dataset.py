"""Validate generated files, event time, hashes and truth join without a server."""
import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
from prepare_round import sha


def check(folder):
    m=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    for name,expected in m['files'].items():
        if Path(name).name!=name:raise ValueError('Unsafe manifest filename')
        if sha(folder/name)!=expected:raise ValueError(f'Hash mismatch: {name}')
    n=0;prev=None;first=last=None;origins=Counter();ids=set()
    lo=datetime.fromisoformat(m['start_inclusive']);hi=datetime.fromisoformat(m['end_exclusive'])
    with (folder/'events.bulk.ndjson').open(encoding='utf-8') as f, (folder/'truth.jsonl').open(encoding='utf-8') as truth:
        while True:
            action=f.readline()
            if not action:break
            action=json.loads(action);body=f.readline()
            if not body:raise ValueError('Missing bulk document')
            d=json.loads(body);t=datetime.fromisoformat(d['timestamp'])
            if list(action)!=['create']:raise ValueError('Non-create bulk operation')
            meta=action['create'];eid=meta['_id']
            if meta['_index']!=m['index'] or not m['index'].startswith('book3-'):raise ValueError('Unexpected index')
            if eid in ids:raise ValueError('Duplicate document id')
            ids.add(eid)
            if not lo<=t<hi or (prev is not None and t<prev):raise ValueError('Invalid event time/order')
            if not d['book3']['synthetic']:raise ValueError('Missing synthetic provenance')
            if '_a' in d or '_t' in d:raise ValueError('Internal truth leaked')
            label=json.loads(truth.readline())
            if label['event_id']!=eid or label['origin'] not in ('scenario','background'):raise ValueError('Truth join mismatch')
            origins[label['origin']]+=1;n+=1;prev=t
            first=first or d['timestamp'];last=d['timestamp']
        if truth.readline():raise ValueError('Extra truth rows')
    if n!=m['total'] or dict(origins)!=m['counts']:raise ValueError('Count mismatch')
    return {'status':'pass','events':n,'counts':dict(origins),'first_timestamp':first,'last_timestamp':last,'chronological':True,'hashes_verified':True,'network_operations':0}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('folder',type=Path);a=ap.parse_args()
    print(json.dumps(check(a.folder),ensure_ascii=False,indent=2))
