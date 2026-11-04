"""Chapter 3 queries, fixed to the independently generated R02 dataset."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'examples/chapter03';OUT.mkdir(parents=True,exist_ok=True)
INDEX='book3-r02-ch03';A='142.66.143.170';B='221.49.17.120'
WINDOW={'range':{'timestamp':{'gte':'2026-08-03T00:00:00+09:00','lt':'2026-11-01T00:00:00+09:00'}}}
def term(f,v):return {'term':{f:v}}
WEB=term('decoder.name','web-accesslog');NOTFOUND=term('data.id','404')
def card(f):return {'cardinality':{'field':f,'precision_threshold':40000}}
def terms(f,size=5,order=None):
    v={'terms':{'field':f,'size':size}}
    if order:v['terms']['order']=order
    return v
def request(filters,aggs=None,**other):
    v={'size':0,'query':{'bool':{'filter':[WINDOW]+filters}}}
    if aggs:v['aggs']=aggs
    return dict(v,**other)
Q={}
def add(n,title,body):Q[f'{n:02}']={'title':title,'method':'GET','path':'/'+INDEX+'/_search','body':body}
add(1,'전체 자료와 로그 출처',request([],{'sources':terms('decoder.name',15)},track_total_hits=True))
top=terms('data.srcip',5);top['aggs']={'ua':terms('data.user_agent',1)}
add(2,'웹 요청량 상위 출발지',request([WEB],{'by_ip':top}))
wide=terms('data.srcip',5,{'urls':'desc'});wide['aggs']={'urls':card('data.url'),'hosts':card('data.vhost')}
add(3,'404 출발지의 경로와 서비스 다양성',request([WEB,NOTFOUND],{'by_ip':wide}))
paths=terms('data.url',5,{'ips':'desc'});paths['aggs']={'ips':card('data.srcip')}
add(4,'neobank API 경로별 출발지',request([WEB,NOTFOUND,term('data.vhost','neobank.kt66.lab'),{'prefix':{'data.url':'/api/'}}],{'by_url':paths}))
fw=terms('data.srcip',5,{'ports':'desc'});fw['aggs']={'ports':card('data.dstport'),'destinations':card('data.dstip'),'days':{'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1}}}
add(5,'방화벽 출발지별 포트와 목적지',request([term('decoder.name','kt66-nft')],{'by_ip':fw}))
add(6,'웹 후보의 활동 날짜와 응답',request([WEB,term('data.srcip',B)],{'days':{'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','format':'yyyy-MM-dd','min_doc_count':1},'aggs':{'status':terms('data.id',5)}}}))
add(7,'방화벽 후보의 시간순 원문',request([term('decoder.name','kt66-nft'),term('data.srcip',A)],size=6,sort=[{'timestamp':'asc'}],_source=['timestamp','data.srcip','data.dstip','data.dstport','data.action','full_log']))
add(8,'단일 출발지의 웹 경로 원문',request([WEB,term('data.srcip',B)],size=6,sort=[{'timestamp':'asc'}],_source=['timestamp','data.srcip','data.url','data.id','data.vhost','data.user_agent']))
hidden={'terms':{'data.url':['/api/v1/admin/users','/api/v1/accounts/export?format=csv']}}
counts=terms('data.srcip',5);counts['aggs']={'paths':card('data.url')}
add(9,'두 API 경로의 고유 출발지와 IP당 요청',request([WEB,NOTFOUND,term('data.vhost','neobank.kt66.lab'),hidden],{'sources':card('data.srcip'),'by_ip':counts},track_total_hits=True))
for n,q in Q.items():
    (OUT/f'Q03-03-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(len(Q),'queries')
