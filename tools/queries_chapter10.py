"""R10: change events, independent impact observations and coverage."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter10';OUT.mkdir(parents=True,exist_ok=True);Q={}
def t(f,v):return {'term':{f:v}}
def both(*xs):return {'bool':{'filter':list(xs)}}
def terms(f,n=20):return {'terms':{'field':f,'size':n}}
def m(op,f):return {op:{'field':f}}
FIM={'prefix':{'decoder.name':'syscheck'}};WEB=t('decoder.name','web-accesslog');GOV=t('agent.name','govportal');GPU=t('data.src_ip','10.20.50.60');FLOW=t('data.event_type','flow')
def add(n,title,filters,aggs=None,start='2026-08-03T00:00:00+09:00',end='2026-11-01T00:00:00+09:00',**kw):
 b={'size':0,'track_total_hits':True,'query':both({'range':{'timestamp':{'gte':start,'lt':end}}},*filters)}
 if aggs:b['aggs']=aggs
 b.update(kw);Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-r10-ch10/_search','body':b}
v={'date_histogram':{'field':'timestamp','fixed_interval':'10m','time_zone':'+09:00','min_doc_count':1},'aggs':{'hosts':terms('agent.name',20)}}
add(1,'최근 사흘의 FIM 10분 구간과 호스트',[FIM],{'times':v},start='2026-10-29T00:00:00+09:00')
v={'filters':{'filters':{'locked_added':both({'wildcard':{'syscheck.path':'*.kt66lock'}},t('syscheck.event','added')),'note_added':both({'wildcard':{'syscheck.path':'*README_RESTORE.txt'}},t('syscheck.event','added')),'original_deleted':both({'wildcard':{'syscheck.path':'*.hwp'}},t('syscheck.event','deleted'))}},'aggs':{'paths':m('cardinality','syscheck.path'),'first':m('min','timestamp'),'last':m('max','timestamp')}}
add(2,'같은 폴더와 시간의 종류별 이벤트 및 고유 경로',[FIM,GOV,{'prefix':{'syscheck.path':'/srv/share/minwon/'}}],{'kinds':v},start='2026-10-30T03:00:00+09:00',end='2026-10-30T03:20:00+09:00')
add(3,'첫 파일 추가와 삭제 및 안내문 원문',[FIM,GOV,{'prefix':{'syscheck.path':'/srv/share/minwon/'}}],start='2026-10-30T03:00:00+09:00',end='2026-10-30T03:20:00+09:00',size=8,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','syscheck','full_log'])
v={'date_histogram':{'field':'timestamp','fixed_interval':'5m','time_zone':'+09:00','min_doc_count':0},'aggs':{'status':terms('data.id',10)}}
add(4,'neobank 장애 전후의 요청 수와 응답 코드',[WEB,t('data.vhost','neobank.kt66.lab')],{'times':v},start='2026-10-29T13:00:00+09:00',end='2026-10-29T16:00:00+09:00',size=30,sort=[{'timestamp':'asc'}],_source=['timestamp','data','full_log'])
v={'date_histogram':{'field':'timestamp','fixed_interval':'1h','time_zone':'+09:00','min_doc_count':1},'aggs':{'avg':m('avg','data.bytes'),'min':m('min','data.bytes'),'max':m('max','data.bytes')}}
add(5,'같은 첫 화면 200 응답의 시간별 크기',[WEB,t('data.vhost','mediforum.kt66.lab'),t('data.url','/'),t('data.id','200')],{'times':v},start='2026-10-30T00:00:00+09:00')
add(6,'첫 화면 파일 변경 원문',[FIM,t('agent.name','mediforum'),t('syscheck.path','/var/www/mediforum/templates/index.html')],start='2026-10-31T00:00:00+09:00',size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','syscheck','full_log'])
v=terms('data.dest_port',20);v['aggs']={'age':m('sum','data.flow.age'),'destinations':terms('data.dest_ip',20),'apps':terms('data.app_proto',10),'days':{'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1}}}
add(7,'GPU 호스트의 포트별 기간과 연결 시간 합',[FLOW,GPU],{'ports':v})
v={'date_histogram':{'field':'timestamp','fixed_interval':'1h','time_zone':'+09:00','min_doc_count':1}}
add(8,'3333 연결의 실제 시각과 시간대',[FLOW,GPU,t('data.dest_port','3333')],{'times':v},size=3,sort=[{'timestamp':'asc'}],_source=['timestamp','data'])
v=terms('data.query',30);v['aggs']={'types':terms('data.qtype',10)}
add(9,'같은 GPU 주소의 DNS 요청',[t('decoder.name','kt66-dns'),t('data.srcip','10.20.50.60')],{'names':v},size=3,sort=[{'timestamp':'asc'}],_source=['timestamp','data','full_log'])
for n,q in Q.items():(OUT/f'Q03-10-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
