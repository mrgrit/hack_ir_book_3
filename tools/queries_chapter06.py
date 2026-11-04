"""R06: rotate grouping axes and keep mail views distinct from all URLs."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter06';OUT.mkdir(parents=True,exist_ok=True);Q={}
def term(f,v):return {'term':{f:v}}
def terms(f,n=10):return {'terms':{'field':f,'size':n}}
def metric(op,f):return {op:{'field':f}}
AUTH=term('data.app','webmail');FAIL=term('data.result','fail');OK=term('data.result','success')
EXTERNAL={'bool':{'must_not':[{'prefix':{'data.srcip':'10.'}}]}}
def add(n,title,filters,aggs=None,**kwargs):
    body={'size':0,'track_total_hits':True,'query':{'bool':{'filter':[{'range':{'timestamp':{'gte':'2026-08-03T00:00:00+09:00','lt':'2026-11-01T00:00:00+09:00'}}}]+filters}}}
    if aggs:body['aggs']=aggs
    body.update(kwargs);Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-r06-ch06/_search','body':body}
add(1,'출발 IP별 인증 실패',[AUTH,FAIL],{'ips':terms('data.srcip',5)})
v=terms('data.srcuser',300);v['terms']['order']={'_key':'asc'};v['aggs']={'ips':metric('cardinality','data.srcip')}
add(2,'계정별 실패 문서와 고유 출발지',[AUTH,FAIL],{'users':v})
v=terms('data.srcuser',300);v['aggs']={'ips':terms('data.srcip',10),'unique_ips':metric('cardinality','data.srcip')}
add(3,'실습 내부망 밖에서 성공한 계정',[AUTH,OK,EXTERNAL],{'users':v})
v=terms('data.srcuser',10);v['aggs']={'countries':terms('GeoLocation.country_name',10)}
add(4,'국가 값이 있는 해외 성공 후보',[AUTH,OK,{'exists':{'field':'GeoLocation.country_name'}},{'bool':{'must_not':[term('GeoLocation.country_name','Republic of Korea')]}}],{'users':v})
v=terms('data.from_domain',20);v['terms']['order']={'_key':'asc'};v['aggs']={'recipients':metric('cardinality','data.to')}
add(5,'수신 메일의 발신 도메인 전체 분포',[term('data.direction','in'),term('data.status','sent')],{'domains':v})
add(6,'유사 도메인의 시간 범위와 수신자',[term('data.direction','in'),term('data.status','sent'),term('data.from_domain','kt66-lab.help')],{'first':metric('min','timestamp'),'last':metric('max','timestamp'),'recipients':terms('data.to',50),'senders':terms('data.from',5)})
add(7,'lee.yuna의 실습 외부 성공 원문',[AUTH,OK,EXTERNAL,term('data.srcuser','lee.yuna')],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','data.srcuser','data.srcip','data.result','GeoLocation.country_name','full_log'])
v=terms('data.srcip',10);v['aggs']={'urls':metric('cardinality','data.url'),'first':metric('min','timestamp'),'last':metric('max','timestamp'),'status':terms('data.id',5)}
VIEW=[term('data.vhost','webmail.kt66.lab'),term('decoder.name','web-accesslog'),{'prefix':{'data.url':'/?_task=mail&_action=show&_uid='}}]
add(8,'메일 표시 경로의 출발지와 시간 범위',VIEW,{'ips':v})
add(9,'피싱 후보 출발지의 메일 표시 원문',VIEW+[term('data.srcip','102.225.118.252')],size=3,sort=[{'timestamp':'asc'}],_source=['timestamp','data.srcip','data.url','data.id','data.bytes','full_log'])
for n,q in Q.items():(OUT/f'Q03-06-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
