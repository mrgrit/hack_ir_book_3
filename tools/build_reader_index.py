"""Build exact, source-backed reader indexes for all 13 chapters."""
import csv,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/appendixA';OUT.mkdir(parents=True,exist_ok=True)
queries=[];commands=[];sources={}
for chapter in range(1,14):
 source=ROOT/f'manuscript/volume03-chapter{chapter:02}.json';d=json.loads(source.read_text('utf8'));sources[str(source.relative_to(ROOT)).replace('\\','/')]=hashlib.sha256(source.read_bytes()).hexdigest()
 for section in d['pages']:
  for b in section.get('blocks',[]):
   if b['type']=='command':
    path=ROOT/f'examples/chapter{chapter:02}'/(b['id']+'.sh' if chapter==1 else 'commands.sh')
    assert path.exists() and b['text'] in path.read_text('utf8')
    commands.append([chapter,b['id'],section['title'],b['where'],b['purpose'],str(path.relative_to(ROOT)).replace('\\','/')])
 folder=ROOT/f'examples/chapter{chapter:02}';p=folder/'queries.json'
 if p.exists():
  for n,q in json.loads(p.read_text('utf8')).items():
   name=f'Q03-{chapter:02}-{n}.http';assert (folder/name).exists()
   queries.append([chapter,f'Q03-{chapter:02}-{n}',q['title'],q['method'],q['path'],f'examples/chapter{chapter:02}/{name}'])
for name,header,rows in [('query-index.csv',['장','ID','질문','방법','인덱스/경로','파일'],queries),('command-index.csv',['장','ID','절','실행 위치','목적','파일'],commands)]:
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f,lineterminator='\n');w.writerow(header);w.writerows(rows)
(OUT/'index-sources.json').write_text(json.dumps({'chapters':13,'query_files':len(queries),'printed_command_blocks':len(commands),'sources':sources},ensure_ascii=False,indent=2)+'\n','utf8')
print(len(queries),'queries,',len(commands),'commands')
