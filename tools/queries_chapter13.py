"""R15: separate long-lived endpoint activity, AI service access and authorized work."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter13';OUT.mkdir(parents=True,exist_ok=True);Q={}
def t(f,v):return {'term':{f:v}}
def both(*x):return {'bool':{'filter':list(x)}}
def anyof(*x):return {'bool':{'should':list(x),'minimum_should_match':1}}
def terms(f,n=20):return {'terms':{'field':f,'size':n}}
def m(op,f):return {op:{'field':f}}
def days():return {'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1}}
def span():return {'first':m('min','timestamp'),'last':m('max','timestamp')}
def add(n,title,filters,aggs=None,start='2026-08-03T00:00:00+09:00',end='2026-11-01T00:00:00+09:00',**kw):
 b={'size':0,'track_total_hits':True,'query':both({'range':{'timestamp':{'gte':start,'lt':end}}},*filters)}
 if aggs:b['aggs']=aggs
 b.update(kw);Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-r15-ch13/_search','body':b}
WEB=t('decoder.name','web-accesslog');FLOW=t('data.event_type','flow');PC=t('agent.name','KT66-WIN-01')
v=terms('data.win.eventdata.parentProcessName',20);v['aggs']={'children':terms('data.win.eventdata.newProcessName',20)}
add(1,'Windows 부모와 자식 프로세스 조합',[PC,t('data.win.system.eventID','4688')],{'parents':v})
v=terms('data.dest_ip',10);v['aggs']={'days':days(),'up':m('sum','data.flow.bytes_toserver'),**span()}
add(2,'사용자 PC의 외향 연결과 활동 날짜',[FLOW,t('data.src_ip','10.20.70.10')],{'destinations':v})
add(3,'메일 전달과 문서 및 셸 실행',[anyof(both(t('decoder.name','kt66-mailgw'),t('data.from','hr-notice@kt66-hr.support')),both(PC,t('data.win.system.eventID','4688')))],start='2026-09-02T09:40:00+09:00',end='2026-09-02T10:31:00+09:00',size=30,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','data','full_log'])
add(4,'PC발 인증과 관리콘솔 권한 사용',[t('agent.name','adminconsole'),anyof(both(t('decoder.name','sshd'),t('data.srcip','10.20.70.10')),both(t('decoder.name','sudo'),t('data.srcuser','kim.minjun')))],start='2026-10-11T22:14:00+09:00',end='2026-10-11T22:15:00+09:00',size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','decoder.name','data','full_log'])
v=terms('data.domain',20);v['terms']['order']={'names':'desc'};v['aggs']={'names':m('cardinality','data.query'),'sources':terms('data.srcip',5),'types':terms('data.qtype',5),'days':days()}
add(5,'DNS 도메인별 고유 이름과 활동 날짜',[t('decoder.name','kt66-dns')],{'domains':v},size=1,sort=[{'data.query_len':'desc'}],_source=['timestamp','data','full_log'])
v=terms('data.srcip',10);v['terms']['order']={'response_bytes':'desc'};v['aggs']={'response_bytes':m('sum','data.bytes'),**span()}
add(6,'관리콘솔 응답을 많이 받은 출발지',[WEB,t('data.vhost','admin.kt66.lab')],{'sources':v})
aiweb=both(WEB,t('agent.name','aicompanion'),t('data.srcip','138.242.102.64'))
ai=t('data.ai.user','u5520193')
export=both(WEB,t('agent.name','adminconsole'),t('data.srcip','10.20.40.87'),{'prefix':{'data.url':'/api/users/export?'}})
out=both(FLOW,t('data.src_ip','10.20.40.87'),t('data.dest_ip','71.212.10.1'))
v={'filters':{'filters':{'chat':aiweb,'ai':ai,'export':export,'out':out}},'aggs':span()}
add(7,'AI 입력과 내부 응답 및 외부 전송의 시각',[anyof(aiweb,ai,export,out)],{'stages':v,'tools':terms('data.ai.tool',5)},start='2026-10-31T03:00:00+09:00',end='2026-10-31T03:03:00+09:00',size=1,sort=[{'timestamp':'desc'}],_source=['timestamp','data'])
v=terms('data.dest_ip',10);v['terms']['order']={'up':'desc'};v['aggs']={'up':m('sum','data.flow.bytes_toserver'),'sources':terms('data.src_ip',5),'days':days(),**span()}
add(8,'서버의 큰 외향 전송과 정상 백업 후보',[FLOW,{'prefix':{'data.src_ip':'10.20.40.'}},{'range':{'data.flow.bytes_toserver':{'gte':10000000}}},{'bool':{'must_not':[{'prefix':{'data.dest_ip':'10.20.'}}]}}],{'destinations':v})
v=terms('data.srcip',20);v['terms']['order']={'urls':'desc'};v['aggs']={'urls':m('cardinality','data.url'),'agents':terms('data.user_agent',5),**span()}
add(9,'govportal의 404 경로와 점검 후보',[WEB,t('agent.name','govportal'),t('data.id','404')],{'sources':v},size=1,sort=[{'timestamp':'desc'}],_source=['timestamp','data','full_log'])
add(10,'AI 서버발 내보내기 요청 원문',[export],{'urls':m('cardinality','data.url'),'bytes':m('sum','data.bytes'),**span()},start='2026-10-31T03:00:00+09:00',end='2026-10-31T03:03:00+09:00',size=25,sort=[{'timestamp':'asc'}],_source=['timestamp','data','full_log'])
for n,q in Q.items():(OUT/f'Q03-13-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries')
