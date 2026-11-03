"""Prepare a reproducible, chronological purple-agg dataset without SIEM access.

All output goes to a NEW directory. The upstream source stays unchanged.
The only supported durations are 90..365 days until short-window stories are redesigned.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime
import hashlib
import importlib
import json
import math
from pathlib import Path
import re
import sqlite3
import tempfile
import sys

from upstream import COMMIT, load


def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def validate_args(a):
    if not 90<=a.days<=365:
        raise ValueError('Use 90..365 days. Short windows omit or reorder upstream story prerequisites.')
    if not math.isfinite(a.scale) or not 0<a.scale<=1:
        raise ValueError('scale must be finite and in (0, 1]')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,39}',a.run_id):
        raise ValueError('run-id: 1..40 lowercase letters, digits or hyphens')
    if not re.fullmatch(r'r(?:0[1-9]|10|12|13|15)',a.round):
        raise ValueError('Unsupported round')
    datetime.strptime(a.anchor,'%Y-%m-%d')
    if a.out.exists():
        raise FileExistsError('Output directory already exists; choose a new run directory')


def prepare(a):
    validate_args(a)
    p=load(a.source)
    p.DAYS=a.days
    # No engine entry point / Indexer is invoked. Fail closed if an accidental
    # engine networking call is introduced during future maintenance.
    class OfflineOnly:
        def __init__(self,*args,**kwargs):raise RuntimeError('SIEM access disabled in prepare_round')
    p.Indexer=OfflineOnly
    files=list(a.source.glob(a.round+'_*.py'))
    if len(files)!=1:raise ValueError('Expected exactly one round module')
    mod=importlib.import_module(files[0].stem)
    anchor=p._anchor(a.anchor);lower=anchor-a.days*86400
    probe=p.Scenario(anchor,mod.SEED);mod.attack(probe)
    outside=Counter('before_start' if d['_t']<lower else 'at_or_after_end' for d in probe.ev if not lower<=d['_t']<anchor)
    index=f'book3-{a.round}-{a.run_id}'
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='book3-stage-',dir=a.out.parent) as temp:
        stage=Path(temp);db=sqlite3.connect(stage/'sort.sqlite')
        counts=Counter();channels=Counter();inversions=0;prev=float('-inf');dropped=0
        try:
            db.execute('CREATE TABLE events(t REAL, seq INTEGER PRIMARY KEY, origin TEXT, body TEXT)')
            seq=0
            for chunk in p.stream(mod.ROUND,mod.attack,mod.SEED,a.scale,anchor):
                batch=[]
                for d in chunk:
                    t=d.pop('_t');origin='scenario' if d.pop('_a',0) else 'background'
                    inversions+=int(t<prev);prev=t
                    if not lower<=t<anchor:
                        dropped+=1;continue
                    d['book3']={'synthetic':True,'round':a.round,'run_id':a.run_id,'rule_origin':'generator'}
                    counts[origin]+=1;channels[d['decoder']['name']]+=1
                    batch.append((t,seq,origin,canonical(d)));seq+=1
                db.executemany('INSERT INTO events VALUES (?,?,?,?)',batch)
            db.commit()
            publish=stage/'publish';publish.mkdir()
            with (publish/'events.bulk.ndjson').open('w',encoding='utf-8',newline='\n') as events, (publish/'truth.jsonl').open('w',encoding='utf-8',newline='\n') as truth:
                for i,(t,origin,body) in enumerate(db.execute('SELECT t,origin,body FROM events ORDER BY t,seq'),1):
                    event_id=f'{a.round}-{i:09d}'
                    events.write(canonical({'create':{'_index':index,'_id':event_id}})+'\n'+body+'\n')
                    truth.write(canonical({'event_id':event_id,'origin':origin})+'\n')
            template=deepcopy(p.TEMPLATE);template['index_patterns']=[index];template['priority']=310
            (publish/'template.json').write_text(json.dumps(template,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            manifest={'schema_version':1,'source_commit':COMMIT,'round':a.round,'seed':mod.SEED,'days':a.days,'anchor':a.anchor,
                'start_inclusive':p.iso(lower),'end_exclusive':p.iso(anchor),'scale':a.scale,'index':index,
                'generator':'upstream with Windows epoch adapter, disk sort and explicit half-open window',
                'timing_model':'upstream-preserved; aggregate gap unit unresolved; not empirically recalibrated',
                'upstream_profile_sha256':sha(a.source/'profile_2019.json'),
                'counts':dict(counts),'total':sum(counts.values()),'scenario_share':counts['scenario']/max(1,sum(counts.values())),
                'channels':dict(channels),'input_time_inversions':inversions,'stream_outside_window_removed':dropped,
                'scenario_outside_window_before_upstream_filter':dict(outside),
                'truth_definition':'scenario means upstream attack() branch, including authorized scanner/backup; background includes hostile background scanning. Neither is a malicious/benign label.',
                'files':{f.name:sha(f) for f in sorted(publish.iterdir())},
                'network_operations':0,'limitations':['No Wazuh decoder or rule execution.','No SIEM upload or template application.','No PCAP reconstruction or replay.','Scale mostly changes background population; it is not a uniform event sampling probability.','Upstream synthetic GeoLocation is not real IP geolocation.']}
            (publish/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            # Atomic directory publication: partial products never appear as a run.
            # Existing runs are rejected before any work and again at publish time.
            if a.out.exists():raise FileExistsError(a.out)
            publish.rename(a.out)
        finally:
            db.close()
    return manifest


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',required=True,type=Path,help='Unchanged pinned purple-agg directory')
    ap.add_argument('--round',default='r01');ap.add_argument('--anchor',default='2026-11-01')
    ap.add_argument('--days',type=int,default=90);ap.add_argument('--scale',type=float,default=0.005)
    ap.add_argument('--run-id',required=True);ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args()
    try:
        m=prepare(a)
    except (ValueError,FileExistsError) as e:
        ap.error(str(e))
    print(json.dumps({k:m[k] for k in ('index','total','counts','input_time_inversions','scenario_outside_window_before_upstream_filter','network_operations')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
