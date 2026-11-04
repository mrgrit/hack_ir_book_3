"""Separate R03 and R04 requests; no cross-round incident join."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter04';OUT.mkdir(parents=True,exist_ok=True)
Q={}
def term(f,v):return {'term':{f:v}}
def terms(f,n=5):return {'terms':{'field':f,'size':n}}
def metric(op,f):return {op:{'field':f}}
def window(start='2026-08-03',end='2026-11-01'):return {'range':{'timestamp':{'gte':start+'T00:00:00+09:00','lt':end+'T00:00:00+09:00'}}}
WEB=term('decoder.name','web-accesslog');NB=term('data.vhost','neobank.kt66.lab');MED=term('agent.name','mediforum')
X='218.136.73.91';W='70.246.138.5'
def add(n,round,title,filters,aggs=None,start='2026-08-03',end='2026-11-01',**kwargs):
    body={'size':0,'track_total_hits':True,'query':{'bool':{'filter':[window(start,end)]+filters}}}
    if aggs:body['aggs']=aggs
    body.update(kwargs);Q[f'{n:02}']={'title':title,'method':'GET','path':f'/book3-{round}-ch04/_search','body':body}
v=terms('data.srcip',3);v['aggs']={'sites':terms('data.vhost',3)}
add(1,'r03','WAF 기록의 출발지와 서비스',[term('decoder.name','modsecurity')],{'sources':v})
v=terms('data.srcip',3);v['terms']['order']={'blocked':'desc'};v['aggs']={k:{'filter':term('data.id',s)} for k,s in [('blocked','403'),('ok','200'),('error','500')]}
add(2,'r03','서비스를 고정한 응답 코드 비교',[WEB,NB],{'sources':v})
v=terms('data.srcip',3);v['terms']['order']={'maximum':'desc'};v['aggs']={k:metric(op,'data.bytes') for k,op in [('maximum','max'),('average','avg'),('total','sum')]}
add(3,'r03','history 응답 크기 비교',[WEB,NB,{'prefix':{'data.url':'/api/history'}}],{'sources':v})
add(4,'r03','10월 28일의 10분별 응답',[WEB,NB,term('data.srcip',X)],{'time':{'date_histogram':{'field':'timestamp','fixed_interval':'10m','time_zone':'+09:00','format':'MM-dd HH:mm','min_doc_count':1},'aggs':{'status':terms('data.id',6)}}},start='2026-10-28',end='2026-10-29')
add(5,'r03','큰 응답의 실제 요청 원문',[WEB,NB,term('data.srcip',X),{'range':{'data.bytes':{'gte':1000000}}}],size=3,sort=[{'timestamp':'asc'}],_source=['timestamp','data.url','data.id','data.bytes','data.duration_ms','data.srcip'])
add(6,'r04','업로드 폴더에 추가된 파일의 확장자',[term('rule.id','554'),{'wildcard':{'syscheck.path':'/var/www/*/uploads/*'}}],{'extensions':{'filters':{'filters':{ext:{'wildcard':{'syscheck.path':'*.'+ext}} for ext in ['jpg','png','pdf','php']}}}})
v=terms('data.audit.parent',5);v['aggs']={'executables':terms('data.audit.exe',5)}
add(7,'r04','부모 프로세스와 실행 파일',[term('decoder.name','auditd')],{'parents':v})
v=terms('data.srcip',3);v['aggs']={'urls':{'cardinality':{'field':'data.url','precision_threshold':40000}},'first':metric('min','timestamp'),'last':metric('max','timestamp')}
add(8,'r04','업로드 PHP 경로의 호출 출발지',[WEB,MED,{'wildcard':{'data.url':'/uploads/*.php*'}}],{'sources':v})
add(9,'r04','파일 추가와 첫 실행 순서',[MED,{'bool':{'should':[term('data.srcip',W),term('data.audit.parent','/usr/sbin/apache2'),{'wildcard':{'syscheck.path':'*.php'}}],'minimum_should_match':1}}],start='2026-09-22',end='2026-09-23',size=6,sort=[{'timestamp':'asc'}],_source=['timestamp','decoder.name','data.url','syscheck.path','data.audit.parent','data.audit.exe','data.audit.command'])
add(10,'r04','계정과 지속성 관련 파일 원문',[MED,{'bool':{'should':[{'prefix':{'syscheck.path':'/etc/'}},{'prefix':{'syscheck.path':'/root/'}},term('rule.id','5902')],'minimum_should_match':1}}],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','rule.id','syscheck.path','data.dstuser','full_log'])
v=terms('data.audit.exe',3);v['aggs']={'first':metric('min','timestamp'),'last':metric('max','timestamp'),'hosts':{'cardinality':{'field':'agent.name'}}}
add(11,'r04','cron 실행 파일과 관측 기간',[term('data.audit.parent','/usr/sbin/cron')],{'executables':v})
add(12,'r04','의심 예약 작업의 연속 시각',[MED,term('data.audit.parent','/usr/sbin/cron'),term('data.audit.exe','/tmp/.x/update.sh')],size=6,sort=[{'timestamp':'asc'}],_source=['timestamp','data.audit.command','data.audit.auid','data.audit.parent','data.audit.exe'])
for n,q in Q.items():(OUT/f'Q03-04-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
