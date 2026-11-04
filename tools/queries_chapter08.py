"""R08: direction, observed intervals, and domain candidates."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter08';OUT.mkdir(parents=True,exist_ok=True);Q={}
def t(f,v):return {'term':{f:v}}
def terms(f,n=20):return {'terms':{'field':f,'size':n}}
def m(op,f):return {op:{'field':f}}
FLOW=t('data.event_type','flow');PC=t('data.src_ip','10.20.70.10');DNS=t('decoder.name','kt66-dns');DOM=t('data.domain','cdn-sync-analytics.com')
def add(n,title,filters,aggs=None,start='2026-08-03T00:00:00+09:00',end='2026-11-01T00:00:00+09:00',**kw):
    b={'size':0,'track_total_hits':True,'query':{'bool':{'filter':[{'range':{'timestamp':{'gte':start,'lt':end}}}]+filters}}}
    if aggs:b['aggs']=aggs
    b.update(kw);Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-r08-ch08/_search','body':b}
v=terms('data.dest_ip');v['aggs']={'ports':terms('data.dest_port',10),'days':{'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1}}}
add(1,'PC의 목적지와 모든 포트 및 활동 날짜',[FLOW,PC],{'destinations':v})
v={'date_histogram':{'field':'timestamp','fixed_interval':'6h','time_zone':'+09:00','min_doc_count':0}}
add(2,'443 반복 연결의 6시간 분포',[FLOW,PC,t('data.dest_ip','112.177.128.164'),t('data.dest_port','443')],{'times':v})
add(3,'첫 하루 반복 연결 시각 원문',[FLOW,PC,t('data.dest_ip','112.177.128.164'),t('data.dest_port','443')],start='2026-08-13T14:00:00+09:00',end='2026-08-14T14:00:00+09:00',size=30,sort=[{'timestamp':'asc'}],_source=['timestamp','data.src_ip','data.dest_ip','data.dest_port','data.app_proto','data.flow'])
v=terms('data.domain',30);v['aggs']={'names':m('cardinality','data.query'),'length':m('avg','data.query_len'),'sources':terms('data.srcip',250),'types':terms('data.qtype',10)}
add(4,'DNS 도메인별 이름 수와 길이 및 출발지',[DNS],{'domains':v})
v={'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1},'aggs':{'first':m('min','timestamp'),'last':m('max','timestamp'),'names':m('cardinality','data.query')}}
add(5,'긴 이름 후보의 날짜별 집중 범위',[DNS,DOM,t('data.srcip','10.20.70.10')],{'days':v},size=3,sort=[{'timestamp':'asc'}],_source=['timestamp','data','full_log'])
v=terms('data.dest_ip',30);v['terms']['order']={'out_bytes':'desc'};v['aggs']={'out_bytes':m('sum','data.flow.bytes_toserver'),'in_bytes':m('sum','data.flow.bytes_toclient'),'sources':terms('data.src_ip',250)}
add(6,'내부발 연결의 목적지별 방향 바이트 합계',[FLOW,{'prefix':{'data.src_ip':'10.20.'}},{'bool':{'must_not':[{'prefix':{'data.dest_ip':'10.20.'}}]}}],{'destinations':v})
add(7,'대용량 후보 여섯 흐름의 원문',[FLOW,PC,t('data.dest_ip','195.30.10.79')],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','data'])
v=terms('data.dest_port',10);v['aggs']={'destinations':terms('data.dest_ip',20),'sources':terms('data.src_ip',250),'protocols':terms('data.app_proto',10)}
add(8,'사용자존의 포트와 프로토콜 관측',[FLOW,{'prefix':{'data.src_ip':'10.20.70.'}}],{'ports':v})
for n,q in Q.items():(OUT/f'Q03-08-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
