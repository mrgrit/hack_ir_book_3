"""Print a few generated event documents without submitting bulk actions."""
import argparse
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('folder',type=Path)
    ap.add_argument('--decoder',help='Exact decoder.name to inspect')
    ap.add_argument('--limit',type=int,default=1)
    a=ap.parse_args()
    if not 1<=a.limit<=20:ap.error('limit must be 1..20')
    shown=0
    with (a.folder/'events.bulk.ndjson').open(encoding='utf-8') as f:
        while True:
            line=f.readline()
            if not line:break
            meta=json.loads(line)
            body=f.readline()
            if not body:raise ValueError('Missing bulk document')
            doc=json.loads(body)
            if a.decoder and doc['decoder']['name']!=a.decoder:continue
            print(json.dumps({'bulk_action':meta,'event':doc},ensure_ascii=False,indent=2))
            shown+=1
            if shown>=a.limit:break
    if not shown:raise SystemExit('No matching event; check decoder name and dataset')


if __name__=='__main__':main()
