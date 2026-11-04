"""R12 and R13 remain separate datasets; evidence before attribution."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter11';OUT.mkdir(parents=True,exist_ok=True);Q={}
def t(f,v):return {'term':{f:v}}
def both(*x):return {'bool':{'filter':list(x)}}
def either(*x):return {'bool':{'should':list(x),'minimum_should_match':1}}
def terms(f,n=20):return {'terms':{'field':f,'size':n}}
def m(op,f):return {op:{'field':f}}
def add(n,title,r,filters,aggs=None,start='2026-08-03T00:00:00+09:00',end='2026-11-01T00:00:00+09:00',**kw):
 b={'size':0,'track_total_hits':True,'query':both({'range':{'timestamp':{'gte':start,'lt':end}}},*filters)}
 if aggs:b['aggs']=aggs
 b.update(kw);Q[f'{n:02}']={'title':title,'method':'GET','path':f'/book3-r{r}-ch11/_search','body':b}
AI={'exists':{'field':'data.ai.tool'}};USER=t('data.ai.user','u7731042');FLAG=t('data.ai.flags','injection_pattern');WEB=t('decoder.name','web-accesslog');FLOW=t('data.event_type','flow');PRIV={'terms':{'data.ai.tool':['http_fetch','file_read','shell']}}
v=terms('data.ai.tool',20);v['aggs']={'users':m('cardinality','data.ai.user')}
add(1,'R12 도구 표시와 사용자 수',12,[AI],{'tools':v})
v=terms('data.ai.user',5);v['terms']['order']={'max_length':'desc'};v['aggs']={'max_length':m('max','data.ai.prompt_len'),'avg_length':m('avg','data.ai.prompt_len'),'tokens':m('sum','data.ai.tokens_out')}
add(2,'R12 사용자별 길이와 출력 토큰',12,[AI],{'users':v})
add(3,'R12 표지와 차단을 분리한 조건',12,[USER],{'states':{'filters':{'filters':{'flag_blocked':both(FLAG,t('data.ai.blocked','true')),'flag_allowed':both(FLAG,t('data.ai.blocked','false')),'unflagged':{'bool':{'must_not':[FLAG]}}}},'aggs':{'tools':terms('data.ai.tool',10)}}})
add(4,'R12 관리용 도구 표시의 원문',12,[PRIV],{'users':terms('data.ai.user',10)},size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','data'])
add(5,'R12 디버그와 업로드의 경로 및 응답',12,[WEB,t('data.vhost','ai.kt66.lab'),either({'prefix':{'data.url':'/api/debug'}},{'prefix':{'data.url':'/api/docs'}})],size=30,sort=[{'timestamp':'asc'}],_source=['timestamp','data','full_log'])
v=terms('data.src_ip',20);v['aggs']={'ports':terms('data.dest_port',10)}
add(6,'R12 관리콘솔로 향한 관측 출발지',12,[FLOW,t('data.dest_ip','10.20.40.86')],{'sources':v})
add(7,'R12 http_fetch 표시와 내부 연결의 시각',12,[either(both(USER,t('data.ai.tool','http_fetch')),both(FLOW,t('data.src_ip','10.20.40.87'),t('data.dest_ip','10.20.40.86')))],size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','data'])
v={'date_histogram':{'field':'timestamp','fixed_interval':'1m','time_zone':'+09:00','min_doc_count':1},'aggs':{'sources':{'terms':{'field':'data.srcip','size':10},'aggs':{'clients':terms('data.user_agent',10)}}}}
add(8,'R13 특정 서비스의 분당 요청과 출발지',13,[WEB,t('data.vhost','juice.kt66.lab')],{'times':v},start='2026-10-30T04:00:00+09:00',end='2026-10-30T04:15:00+09:00')
X='92.10.220.142'
v={'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1},'aggs':{'first':m('min','timestamp'),'last':m('max','timestamp')}}
add(9,'R13 같은 출발지의 날짜별 범위',13,[WEB,t('data.srcip',X)],{'days':v,'first':m('min','timestamp'),'last':m('max','timestamp'),'clients':terms('data.user_agent',20)})
AUD=both(t('decoder.name','auditd'),t('agent.name','juiceshop'),t('data.audit.parent','/usr/local/bin/node'))
SSH=both(t('decoder.name','sshd'),t('data.srcip','10.20.40.81'))
OUTFLOW=both(FLOW,t('data.src_ip','10.20.40.83'),{'range':{'data.flow.bytes_toserver':{'gte':100000000}}})
v={'date_histogram':{'field':'timestamp','fixed_interval':'1m','time_zone':'+09:00','min_doc_count':1},'aggs':{'kinds':terms('decoder.name',20)}}
add(10,'R13 짧은 본 사건의 관측 종류별 시간표',13,[either(t('data.srcip',X),AUD,SSH,OUTFLOW)],{'times':v},start='2026-10-30T04:10:00+09:00',end='2026-10-30T04:15:00+09:00')
add(11,'R13 프로세스와 서버 인증 및 큰 전송 원문',13,[either(AUD,SSH,OUTFLOW)],start='2026-10-30T04:10:00+09:00',end='2026-10-30T04:15:00+09:00',size=30,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','decoder.name','data','full_log','rule'])
v=terms('data.id',10);v['aggs']={'max_bytes':m('max','data.bytes')}
add(12,'R13 검색 경로의 응답 코드와 큰 응답 원문',13,[WEB,t('data.srcip',X),{'prefix':{'data.url':'/rest/products/search'}}],{'status':v},size=4,sort=[{'data.bytes':'desc'},{'timestamp':'asc'}],_source=['timestamp','data','full_log'])
add(13,'R13 생성 레벨 값과 필드 없는 문서',13,[t('data.srcip',X)],{'levels':terms('rule.level',20),'without_level':{'filter':{'bool':{'must_not':[{'exists':{'field':'rule.level'}}]}}}})
for n,q in Q.items():(OUT/f'Q03-11-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
