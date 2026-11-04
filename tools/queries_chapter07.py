"""R07: distinguish fixed time buckets, host targets, and Windows evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter07';OUT.mkdir(parents=True,exist_ok=True);Q={}
def term(f,v):return {'term':{f:v}}
def terms(f,n=10):return {'terms':{'field':f,'size':n}}
def metric(op,f):return {op:{'field':f}}
BAST=term('data.srcip','10.20.30.201');SSH=term('decoder.name','sshd');WIN=term('agent.name','KT66-WIN-01')
def add(n,title,filters,aggs=None,start='2026-08-03T00:00:00+09:00',end='2026-11-01T00:00:00+09:00',**kwargs):
    body={'size':0,'track_total_hits':True,'query':{'bool':{'filter':[{'range':{'timestamp':{'gte':start,'lt':end}}}]+filters}}}
    if aggs:body['aggs']=aggs
    body.update(kwargs);Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-r07-ch07/_search','body':body}
v=terms('data.srcuser',20);v['aggs']={'hosts':terms('agent.name',10),'unique_hosts':metric('cardinality','agent.name')}
add(1,'bastion발 SSH 성공의 계정과 대상',[SSH,BAST,term('rule.id','5715')],{'users':v})
v={'date_histogram':{'field':'timestamp','fixed_interval':'10m','time_zone':'+09:00','min_doc_count':1},'aggs':{'hosts':terms('agent.name',10),'unique_hosts':metric('cardinality','agent.name')}}
add(2,'kim.minjun 성공의 고정 10분 버킷',[SSH,BAST,term('rule.id','5715'),term('data.srcuser','kim.minjun')],{'times':v},start='2026-10-29T01:00:00+09:00',end='2026-10-29T02:00:00+09:00')
add(3,'여러 서버의 SSH 성공과 실패 원문',[SSH,BAST,term('data.srcuser','kim.minjun'),{'terms':{'rule.id':['5715','5716']}}],start='2026-10-29T01:00:00+09:00',end='2026-10-29T02:00:00+09:00',size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','data.srcip','data.srcuser','rule.id','full_log'])
v=terms('GeoLocation.country_name',10);v['aggs']={'users':terms('data.srcuser',20),'sources':terms('data.srcip',20)}
add(4,'bastion의 외부 성공 출발지',[SSH,term('agent.name','bastion'),term('rule.id','5715'),{'exists':{'field':'GeoLocation.country_name'}}],{'countries':v})
v=terms('data.src_ip',10);w=terms('data.dest_ip',10);w['aggs']={'ports':terms('data.dest_port',20)};v['aggs']={'destinations':w,'first':metric('min','timestamp'),'last':metric('max','timestamp')}
add(5,'서버존 연결의 출발지와 목적지별 포트',[term('data.event_type','flow'),{'prefix':{'data.dest_ip':'10.20.40.'}}],{'sources':v})
v=terms('data.win.eventdata.logonType',10);v['aggs']={'ips':terms('data.win.eventdata.ipAddress',10),'users':terms('data.win.eventdata.targetUserName',20)}
add(6,'Windows 성공 로그온 유형과 출발지',[WIN,term('data.win.system.eventID','4624')],{'types':v})
add(7,'Windows 로그온과 프로세스 및 계정 변경',[WIN,{'terms':{'data.win.system.eventID':['4624','4688','4720','4732']}}],start='2026-10-29T01:30:00+09:00',end='2026-10-29T01:40:00+09:00',size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','data.win.system.eventID','data.win.eventdata'])
add(8,'svc_backup의 후속 네트워크 로그온',[WIN,term('data.win.system.eventID','4624'),term('data.win.eventdata.targetUserName','svc_backup')],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','data.win.eventdata'])
add(9,'neobank에서 Windows로 향한 SMB 연결',[term('data.event_type','flow'),term('data.src_ip','10.20.40.83'),term('data.dest_ip','10.20.70.10'),term('data.dest_port','445')],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','data.src_ip','data.dest_ip','data.dest_port','data.app_proto','data.flow'])
for n,q in Q.items():(OUT/f'Q03-07-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
