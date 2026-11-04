import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter12';OUT.mkdir(parents=True,exist_ok=True);Q={}
def term(f,v):return {'term':{f:v}}
def terms(f,n=20):return {'terms':{'field':f,'size':n}}
def add(n,title,filters,aggs,**kw):
 b={'size':0,'track_total_hits':True,'query':{'bool':{'filter':[{'range':{'timestamp':{'gte':'2025-01-22T19:44:00Z','lt':'2025-01-22T20:39:00Z'}}},*filters]}},'aggs':aggs};b.update(kw)
 Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-pcap-ch12/_search','body':b}
add(1,'선택한 센서 관측의 종류',[],{'kinds':terms('data.event_type'),'first':{'min':{'field':'timestamp'}},'last':{'max':{'field':'timestamp'}}})
v=terms('data.http.hostname');v['aggs']={'methods':terms('data.http.http_method')}
add(2,'HTTP 대상과 요청 방법',[term('data.event_type','http')],{'hosts':v})
add(3,'반복 HTTP 경로의 응답과 누락',[term('data.event_type','http'),term('data.http.url','/1517096937'),term('data.dest_ip','5.252.153.241')],{'status':terms('data.http.status'),'without_status':{'filter':{'bool':{'must_not':[{'exists':{'field':'data.http.status'}}]}}},'flows':{'cardinality':{'field':'data.flow_id'}}},size=2,sort=[{'timestamp':'asc'}],_source=['timestamp','data.timestamp','data.flow_id','data.pcap_cnt','data.tx_id','data.http.status','data.http.url'])
add(4,'후보 목적지의 연결과 방향별 바이트',[term('data.event_type','flow'),term('data.dest_ip','5.252.153.241')],{'to_server':{'sum':{'field':'data.flow.bytes_toserver'}},'to_client':{'sum':{'field':'data.flow.bytes_toclient'}}},size=5,sort=[{'data.flow.start':'asc'}],_source=['timestamp','data.flow_id','data.src_ip','data.src_port','data.dest_ip','data.dest_port','data.flow'])
add(5,'DNS 요청과 응답의 관측 단위',[term('data.event_type','dns')],{'message_kind':terms('data.dns.type')})
add(6,'관측용 GET 경보와 실제 Wazuh 규칙의 구분',[term('data.event_type','alert')],{'signatures':terms('data.alert.signature_id')},size=1,sort=[{'timestamp':'asc'}],_source=['timestamp','data.event_type','data.http.hostname','data.http.url','data.alert'])
for n,q in Q.items():(OUT/f'Q03-12-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
