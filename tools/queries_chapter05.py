"""R05 evidence queries with explicit empty time buckets and host scope."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter05';OUT.mkdir(parents=True,exist_ok=True);Q={}
def term(f,v):return {'term':{f:v}}
def terms(f,n=5):return {'terms':{'field':f,'size':n}}
def metric(op,f):return {op:{'field':f}}
MED=term('agent.name','mediforum');AUDIT=term('decoder.name','auditd');SUDO=term('decoder.name','sudo')
def add(n,title,filters,aggs=None,start='2026-08-03T00:00:00+09:00',end='2026-11-01T00:00:00+09:00',**kwargs):
    body={'size':0,'track_total_hits':True,'query':{'bool':{'filter':[{'range':{'timestamp':{'gte':start,'lt':end}}}]+filters}}}
    if aggs:body['aggs']=aggs
    body.update(kwargs);Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-r05-ch05/_search','body':body}
v=terms('data.srcuser',20);v['terms']['order']={'_key':'asc'};v['aggs']={'results':terms('rule.id',3)}
add(1,'sudo 사용자와 결과 구분',[SUDO],{'users':v})
add(2,'서비스 계정 sudo 원문',[SUDO,MED,term('data.srcuser','www-data')],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','data.srcuser','data.dstuser','data.command','rule.id','full_log'])
add(3,'공백 전 감사 원문',[AUDIT,MED,{'terms':{'data.audit.auid':['root','www-data']}}],start='2026-10-30T00:30:00+09:00',end='2026-10-30T01:00:00+09:00',size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','data.audit.auid','data.audit.exe','data.audit.command','data.audit.parent'])
hist={'date_histogram':{'field':'timestamp','fixed_interval':'1h','time_zone':'+09:00','min_doc_count':0,'extended_bounds':{'min':'2026-10-30T00:00:00+09:00','max':'2026-10-30T03:00:00+09:00'}}}
add(4,'고정된 두 호스트의 시간별 문서 수',[],{'hosts':{'filters':{'filters':{'mediforum':MED,'neobank':term('agent.name','neobank')}},'aggs':{'hours':hist}}},start='2026-10-30T00:00:00+09:00',end='2026-10-30T04:00:00+09:00')
add(5,'에이전트 중지와 시작 명령 기록',[AUDIT,MED,{'prefix':{'data.audit.command':'systemctl '}}],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','data.audit.command','data.audit.auid','data.audit.parent'])
v=terms('data.audit.exe',5);v['aggs']={'users':terms('data.audit.auid',3),'parents':terms('data.audit.parent',3),'first':metric('min','timestamp'),'last':metric('max','timestamp')}
add(6,'임시 경로 실행 파일과 반복 관측',[AUDIT,MED,{'bool':{'should':[{'prefix':{'data.audit.exe':'/tmp/'}},{'prefix':{'data.audit.exe':'/dev/shm/'}}],'minimum_should_match':1}}],{'executables':v})
add(7,'삭제된 파일의 경로 분포',[term('rule.id','553')],{'paths':terms('syscheck.path',12)})
add(8,'재개 뒤의 삭제와 수정 원문',[MED,{'terms':{'rule.id':['550','553']}},{'terms':{'syscheck.path':['/root/.bash_history','/home/www-data/.bash_history','/var/log/apache2/mediforum_access.log.1','/var/log/auth.log']}}],start='2026-10-30T03:00:00+09:00',end='2026-10-30T04:00:00+09:00',size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','syscheck.path','syscheck.event','rule.id','full_log'])
for n,q in Q.items():(OUT/f'Q03-05-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
