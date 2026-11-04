import json
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter02';OUT.mkdir(parents=True,exist_ok=True)
idx='book3-r01-pilot01';c2='53.81.8.74'
window={'range':{'timestamp':{'gte':'2026-08-03T00:00:00+09:00','lt':'2026-11-01T00:00:00+09:00'}}}
def q(extra=None,aggs=None,**kwargs):
 b={'size':0,'query':{'bool':{'filter':[window]+(extra or [])}}}
 if aggs:b['aggs']=aggs
 b.update(kwargs);return b
def terms(field,size=15):return {'terms':{'field':field,'size':size}}
def term(field,value):return {'term':{field:value}}
queries={}
def add(n,title,b,endpoint=None):
 queries[n]={'title':title,'method':'GET','path':endpoint or '/'+idx+'/_search','body':b}
add('01','자료 건수와 시간 범위',q(aggs={'first':{'min':{'field':'timestamp'}},'last':{'max':{'field':'timestamp'}}},track_total_hits=True))
add('02','필드 자료형',None,'/'+idx+'/_field_caps?fields=*')
add('03','이벤트 출처별 건수',q(aggs={'by_agent':terms('agent.name')}))
v=terms('data.vhost',10);v['aggs']={'visitors':{'cardinality':{'field':'data.srcip','precision_threshold':40000}},'bytes':{'sum':{'field':'data.bytes'}},'avg_bytes':{'avg':{'field':'data.bytes'}}}
add('04','웹 서비스별 요청과 방문 출발지',q([term('decoder.name','web-accesslog')],{'by_vhost':v}))
add('05','HTTP 응답별 건수',q([term('decoder.name','web-accesslog')],{'by_status':{'filters':{'filters':{'ok':term('data.id','200'),'forbidden':term('data.id','403'),'not_found':term('data.id','404')}},'aggs':{'visitors':{'cardinality':{'field':'data.srcip','precision_threshold':40000}}}}}))
hist={'field':'timestamp','fixed_interval':'7d','time_zone':'+09:00','format':'yyyy-MM-dd','min_doc_count':0,'extended_bounds':{'min':'2026-08-03T00:00:00+09:00','max':'2026-10-31T23:59:59+09:00'}}
hist['extended_bounds']={k:int(datetime.fromisoformat(v).timestamp()*1000) for k,v in hist['extended_bounds'].items()}
add('06','7일 구간별 추이',q(aggs={'per_week':{'date_histogram':hist}}))
dst=terms('data.dest_ip',50);dst['aggs']={'srcs':{'cardinality':{'field':'data.src_ip','precision_threshold':40000}},'active_days':{'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1}}}
server=[{'prefix':{'data.src_ip':'10.20.40.'}}]
add('07','서버존 출발 목적지와 활동 일수',q(server,{'by_dst':dst}))
candidate=server+[term('data.dest_ip',c2)]
day={'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','format':'yyyy-MM-dd','min_doc_count':1,'order':{'_count':'desc'}}
add('08','후보 목적지의 일별 건수',q(candidate,{'per_day':{'date_histogram':day}}))
url=terms('data.http.url',10);method=terms('data.http.http_method',5);method['aggs']={'ua':terms('data.http.http_user_agent',10)};url['aggs']={'method':method}
add('09','요청 경로와 메서드 및 사용자 에이전트',q(candidate,{'by_url':url}))
add('10','급증 구간의 시간순 원문',{'size':8,'_source':['timestamp','agent.name','data.src_ip','data.dest_ip','data.dest_port','data.http'],'sort':[{'timestamp':'asc'}],'query':{'bool':{'filter':[term('data.src_ip','10.20.40.81'),term('data.dest_ip',c2),term('data.http.url','/beat'),{'range':{'timestamp':{'gte':'2026-10-30T10:30:00+09:00','lt':'2026-10-30T10:40:00+09:00'}}}]}}})
selected=json.loads(json.dumps(dst));selected['aggs']['candidate']={'bucket_selector':{'buckets_path':{'n':'_count','s':'srcs'},'script':'params.n >= 500 && params.s == 1'}}
add('11','조건을 넘는 비콘 후보',q(server,{'by_dst':selected}))
add('12','생성기가 부여한 규칙의 분포',q([{'range':{'rule.level':{'gte':7}}}],{'by_rule':terms('rule.description',10)}))
add('13','평소 시간순 원문',{'size':8,'_source':['timestamp','data.src_ip','data.dest_ip','data.http.url'],'sort':[{'timestamp':'asc'}],'query':{'bool':{'filter':[term('data.src_ip','10.20.40.81'),term('data.dest_ip',c2),term('data.http.url','/beat'),{'range':{'timestamp':{'gte':'2026-10-29T00:00:00+09:00','lt':'2026-10-30T00:00:00+09:00'}}}]}}})
add('14','실습 인덱스의 소유 정보',None,'/'+idx+'/_mapping')
for n,r in queries.items():
 text=r['method']+' '+r['path']+'\n'+(json.dumps(r['body'],ensure_ascii=False,indent=2)+'\n' if r['body'] is not None else '')
 (OUT/f'Q03-02-{n}.http').write_text(text,encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('queries',len(queries))
