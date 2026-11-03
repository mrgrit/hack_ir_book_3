"""Read-only offline probes of a pinned purple-agg checkout. No SIEM calls."""
import argparse
from collections import Counter
import hashlib
import importlib
import json
from pathlib import Path
import sys


def run(source):
    from upstream import load
    p=load(source)
    rounds=[importlib.import_module(f.stem) for f in sorted(source.glob('r[0-9][0-9]_*.py'))]
    results=[]
    for days in (7,30,90,365):
        p.DAYS=days
        for mod in rounds:
            s=p.Scenario(p._anchor('2026-11-01'),mod.SEED)
            mod.attack(s)
            results.append({'round':mod.ROUND,'days':days,'scenario_events':len(s.ev),
                'before_window':sum(d['_t']<s.t0 for d in s.ev),
                'at_or_after_anchor':sum(d['_t']>=s.anchor for d in s.ev),
                'channels':dict(Counter(d['decoder']['name'] for d in s.ev))})
    p.DAYS=90
    stream=[]
    for rid in ('r01','r02','r08','r15'):
        mod=next(m for m in rounds if m.ROUND==rid)
        prev=float('-inf'); inversions=0; total=0; scenario=0; early=late=0
        lower=p._anchor('2026-11-01')-90*86400
        for chunk in p.stream(mod.ROUND,mod.attack,mod.SEED,0.005,p._anchor('2026-11-01'),getattr(mod,'NORMAL_OPTS',None),getattr(mod,'tweak',None)):
            for d in chunk:
                inversions+=int(d['_t']<prev);prev=d['_t'];total+=1;scenario+=int(d.get('_a',0))
                early+=int(d['_t']<lower);late+=int(d['_t']>=p._anchor('2026-11-01'))
        stream.append({'round':rid,'days':90,'scale':0.005,'total':total,'scenario_tagged':scenario,'cross_chunk_time_inversions':inversions,'before_window':early,'at_or_after_anchor':late})
    return {'source_commit':'d6a2397fc31517147ddd09f58e0d153bc8cf0588','anchor':'2026-11-01T00:00:00+09:00',
        'method':'Called attack() for 13 rounds at 4 periods; streamed 4 rounds at scale 0.005. No Indexer, socket, replay, HTTP or PCAP execution.',
        'scenario_windows':results,'streams':stream,
        'files':{str(f.relative_to(source)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(source.rglob('*')) if f.is_file() and '__pycache__' not in str(f)}}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    report=run(a.source);a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({'window_failures':[r for r in report['scenario_windows'] if r['before_window'] or r['at_or_after_anchor']], 'streams':report['streams']},ensure_ascii=False))
