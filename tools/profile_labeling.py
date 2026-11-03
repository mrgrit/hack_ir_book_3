"""Read aggregate XLSX snapshots; export statistics only, never source identifiers.

Requires openpyxl for read-only input. Duplicate headers must be acknowledged.
The XLSX stores aggregates, not a recoverable event timeline.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re


def number(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def date(value):
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def quantiles(values):
    v=sorted(x for x in values if x is not None)
    if not v:
        return {'n':0}
    return {'n':len(v), **{f'p{p:02}':round(v[round((len(v)-1)*p/100)],6) for p in (0,10,50,90,99,100)}}


def summarize(rows):
    classes=Counter()
    valid=[]; ratios={k:[] for k in ('span_over_gap_log_line','span_over_gap_log_line_minus_one','span_over_gap_log_len_minus_one')}
    start_hours=Counter(); minute_zero=0; second_zero=0; starts=0
    for r in rows:
        dc=number(r.get('day_cnt'))
        if dc is None or dc<1:
            classes['invalid']+=1
        else:
            classes['oneshot' if dc<=1 else 'returning' if dc<15 else 'persistent']+=1
        s,e=date(r.get('log_start')),date(r.get('log_end'))
        if s:
            starts+=1; start_hours[s.hour]+=1
            minute_zero+=int(s.minute==0 and s.second==0)
            second_zero+=int(s.second==0)
        if s and e and e>=s:
            span=(e-s).total_seconds()
            valid.append(span/86400)
            gap=number(r.get('mean_tg')); ll=number(r.get('log_line')); n=number(r.get('log_len'))
            if gap and span:
                for name,denom in [('span_over_gap_log_line',ll),('span_over_gap_log_line_minus_one',ll-1 if ll else None),('span_over_gap_log_len_minus_one',n-1 if n else None)]:
                    if denom and denom>0:
                        ratios[name].append(span/(gap*denom))
    fields=('log_line','log_len','day_cnt','dip_cnt','hour_dist','nwt_ratio','hd_ratio','mean_tg','stdev_tg')
    return {
        'rows':len(rows),'class_counts':dict(classes),
        'class_definition':'day_cnt <= 1; 1 < day_cnt < 15; day_cnt >= 15. Activity classes, not malicious labels.',
        'class_share':{k:round(v/len(rows),6) for k,v in classes.items()} if rows else {},
        'metrics':{k:quantiles(number(r.get(k)) for r in rows) for k in fields},
        'span_days':quantiles(valid),
        'start_hour_counts':[start_hours[h] for h in range(24)],
        'start_precision':{'valid':starts,'exact_hour':minute_zero,'exact_minute':second_zero},
        'interval_unit_diagnostics':{k:{**quantiles(v),'near_60_ratio_count':sum(abs(x-60)<0.01 for x in v),'near_1_ratio_count':sum(abs(x-1)<0.0002 for x in v)} for k,v in ratios.items()},
        'time_zone':'not declared in spreadsheet datetime cells; do not assume KST',
        'gap_unit':'unconfirmed; ratio diagnostics are evidence, not a recovered field definition',
    }


def read_snapshot(path, duplicate_policy):
    import openpyxl
    wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
    try:
        ws=wb.active; it=ws.iter_rows(values_only=True); header=next(it)
        duplicates={k:n for k,n in Counter(x for x in header if x).items() if n>1}
        if duplicates and duplicate_policy!='last':
            raise ValueError(f'{path.name}: duplicate columns {duplicates}; explicitly pass --duplicate-column last after reviewing the schema')
        positions={k:i for i,k in enumerate(header) if k}
        required={'ip','log_start','log_end','day_cnt','log_len'}
        if not required<=positions.keys():
            raise ValueError(f'{path.name}: missing columns {sorted(required-positions.keys())}')
        rows=[]
        for values in it:
            row={k:values[i] for k,i in positions.items()}
            if row.get('ip'):
                rows.append(row)
        return rows, {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sheet':ws.title,'rows':len(rows),'duplicate_headers':duplicates,'column_selection':duplicate_policy,'columns':list(positions)}
    finally:
        wb.close()


def analyze(paths, duplicate_policy):
    latest={}; snapshots=[]
    # Filenames establish snapshot ordering, never caller argument order.
    for path in sorted(paths,key=lambda p:p.name):
        rows,meta=read_snapshot(path,duplicate_policy)
        meta['statistics']=summarize(rows); snapshots.append(meta)
        for r in rows:
            k=str(r['ip'])
            rank=(date(r.get('log_end')) or datetime.min,path.name)
            if k not in latest or rank>latest[k][0]:
                latest[k]=(rank,r)
    return {'schema_version':1,'input_kind':'per-source aggregates / cumulative snapshots',
            'privacy':'No IPs, domains, organizations or row-level values exported.',
            'snapshots':snapshots,'latest_per_source':summarize([v[1] for v in latest.values()]),
            'merge_policy':'Union of sources; latest log_end then lexicographic dated filename. This is not a same-date cohort or a sum of daily events.',
            'limitations':['Only the explicitly selected files were inspected.','Aggregate snapshots cannot reconstruct individual interarrival times.','Source selection is security-observation biased; activity class is not an attack label.','Counter.ipynb does not define the aggregate calculations.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('files',nargs='+',type=Path)
    ap.add_argument('--duplicate-column',choices=['reject','last'],default='reject')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    report=analyze(a.files,a.duplicate_column)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({'output':str(a.out),'snapshots':[(s['file'],s['rows']) for s in report['snapshots']], 'unique_sources':report['latest_per_source']['rows']},ensure_ascii=False))


if __name__=='__main__':
    main()
