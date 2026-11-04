"""Build public run records from local manifests; never copy event payloads."""
import csv, hashlib, json, platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'examples/appendixB'
RUNS=[(1,'r01-pilot01'),(3,'r02-ch03'),(4,'r03-ch04'),(4,'r04-ch04'),(5,'r05-ch05'),(6,'r06-ch06'),(7,'r07-ch07'),(8,'r08-ch08'),(9,'r09-ch09'),(10,'r10-ch10'),(11,'r12-ch11'),(11,'r13-ch11'),(13,'r15-ch13'),(12,'pcap-ch12')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf8')
def csvfile(name,head,rows):
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(head);w.writerows(rows)
def main():
 OUT.mkdir(parents=True,exist_ok=True);catalog=[];rows=[]
 for chapter,folder in RUNS:
  path=ROOT/'build'/folder/'manifest.json';m=json.loads(path.read_text('utf8'))
  for name,digest in m['files'].items():assert sha(path.parent/name)==digest,(folder,name)
  catalog.append({'chapter':chapter,'folder':f'build/{folder}','manifest_sha256':sha(path),'manifest':m})
  rows.append([str(chapter) if chapter!=1 else '1/2',m['index'],m.get('round','PCAP'),m.get('seed',''),m.get('days',''),m.get('scale',''),m['total'],m.get('counts',{}).get('background',''),m.get('counts',{}).get('scenario',''),m['files']['events.bulk.ndjson']])
 save(OUT/'run-catalog.json',{'schema_version':1,'runs':catalog,'note':'Manifests only. scenario/background are code provenance, not malicious/benign labels.'})
 csvfile('run-catalog.csv',['장','index','round','seed','days','scale','total','background','scenario','bulk_sha256'],rows)
 before=ROOT/'build/r15-ch13';after=ROOT/'build/repro-b/r15-ch13';comparison={}
 for name in ['manifest.json','events.bulk.ndjson','template.json','truth.jsonl']:
  a=sha(before/name);z=sha(after/name);assert a==z,name;comparison[name]={'sha256':a,'identical':True}
 result={'status':'pass','scope':'Local offline R15 reproduction; no server calls or packets transmitted','runtime':{'python':platform.python_version(),'platform':platform.system()},'source_commit':catalog[-2]['manifest']['source_commit'],'parameters':{k:catalog[-2]['manifest'][k] for k in ['round','seed','anchor','days','scale','index']},'output_folders':['build/r15-ch13','build/repro-b/r15-ch13'],'events':105293,'files':comparison,'tool_sha256':{f:sha(ROOT/f) for f in ['tools/prepare_round.py','tools/upstream.py','tools/check_dataset.py']},'catalog_runs':len(catalog),'synthetic_total':sum(r['manifest']['total'] for r in catalog if 'round' in r['manifest']),'pcap_documents':3746,'network_operations':0}
 save(ROOT/'editorial/appendixB-reproduction-verification.json',result)
 save(OUT/'reproduction-record.json',{'schema_version':1,'record_status':'blank-template','source_kind':None,'source_url':None,'source_commit':None,'book_commit':None,'input_sha256':{},'runtime':{'os':None,'python':None,'sensor_version':None,'container_digest':None},'parameters':{'round':None,'seed':None,'anchor':None,'days':None,'scale':None,'run_id':None,'start_inclusive':None,'end_exclusive':None,'time_zone':None},'sensor':{'config_sha256':None,'rules_sha256':None,'overrides':[],'selected_event_types':[]},'outputs':{'folder':None,'index':None,'total':None,'files_sha256':{}},'verification':{'commands':[],'counts':{},'failed_checks':[],'evidence_files':[]},'scope':{'packets_transmitted':None,'manager_rule_execution':None,'siem_loaded':None,'retained_resources':[],'cleanup_record':None},'unknowns':[]})
 csvfile('distribution-check.csv',['metric','unit','denominator','window_and_filter','reference','generated','missing','method','decision','limitation'],[
 ['활동 일수','일/출발지','같은 관측 범위의 출발지','','','','','활동한 서로 다른 날짜를 센다','',''],
 ['이벤트 수','건/시간 창','같은 대상·창의 이벤트','','','','','동일 경계의 시간 창으로 센다','',''],
 ['세션 내 간격','초','같은 세션의 인접 이벤트 쌍','','','','','시간순 차분. 연결 전환·결측은 별도 기록','',''],
 ['승인 작업 오탐','건/승인 작업','독립 승인 기록이 있는 작업','','','','','승인 범위와 관측·탐지 결과를 대조한다','','']])
 # Korean forms are filled without publishing original identifiers or private logs.
 csvfile('source-record.csv',['항목','기록'],[(k,'') for k in ['자료명과 원 URL','취득 일시와 담당자','이용 조건 URL과 확인일','ZIP SHA-256','PCAP/원자료 SHA-256','기간·시간대·관측 위치','수집·가공 방법','공개할 메타데이터','식별자 처리와 대응표 보관 위치','보관 위치·접근 권한·기간','배포 범위와 제한','미확인 사항']])
 csvfile('handoff-record.csv',['항목','기록'],[(k,'') for k in ['사건/실습 식별자','전달 목적','발신·수신 담당자','전달 일시와 시간대','원본 보관 위치와 접근 권한','전달 파일명·크기·SHA-256','수신 측 재계산 SHA-256','변경·가공 이력','조회 조건·결과·원문 연결','판정과 추가 증거','남긴 리소스·원상복구 책임','확인 결과와 미확인 사항']])
 print('PASS',len(catalog),'run manifests; R15 identical files',len(comparison),'synthetic total',result['synthetic_total'])
if __name__=='__main__':main()
