"""R09: preserve phases omitted by a broad one-shot chain query."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'examples/chapter09';OUT.mkdir(parents=True,exist_ok=True);Q={}
def t(f,v):return {'term':{f:v}}
def terms(f,n=20):return {'terms':{'field':f,'size':n}}
def m(op,f):return {op:{'field':f}}
def both(*x):return {'bool':{'filter':list(x)}}
def anyof(*x):return {'bool':{'should':list(x),'minimum_should_match':1}}
GOV=t('agent.name','govportal');WEB=t('decoder.name','web-accesslog');FLOW=t('data.event_type','flow');I1='208.162.131.213';I3='142.102.238.6'
def add(n,title,filters,aggs=None,start='2026-08-03T00:00:00+09:00',end='2026-11-01T00:00:00+09:00',**kw):
    b={'size':0,'track_total_hits':True,'query':both({'range':{'timestamp':{'gte':start,'lt':end}}},*filters)}
    if aggs:b['aggs']=aggs
    b.update(kw);Q[f'{n:02}']={'title':title,'method':'GET','path':'/book3-r09-ch09/_search','body':b}
v=terms('data.srcip',20);v['terms']['order']={'blocked':'desc'};v['aggs']={'blocked':{'filter':t('data.id','403')},'ok':{'filter':t('data.id','200')},'max_bytes':m('max','data.bytes')}
add(1,'govportal의 차단 응답이 많은 출발지',[GOV,WEB],{'sources':v})
v=terms('data.id',10);v['aggs']={'first':m('min','timestamp'),'last':m('max','timestamp'),'max_bytes':m('max','data.bytes')}
add(2,'후보의 응답 시각과 큰 응답 원문',[GOV,WEB,t('data.srcip',I1)],{'responses':v},start='2026-09-27T00:00:00+09:00',end='2026-09-28T00:00:00+09:00',size=3,sort=[{'data.bytes':'desc'}],_source=['timestamp','data','full_log'])
shell='/var/www/govportal/files/m_8812.php';cron='/etc/cron.d/backupsvc'
upload=anyof(both(WEB,{'prefix':{'data.url':'/files/m_8812.php'}}),both(WEB,t('data.url','/minwon/apply')),t('data.audit.parent','/usr/sbin/apache2'),t('syscheck.path',shell))
add(3,'웹 요청과 파일 생성 및 셸 실행',[GOV,upload],start='2026-09-28T22:00:00+09:00',end='2026-09-29T00:00:00+09:00',size=30,sort=[{'timestamp':'asc'}],_source=['timestamp','decoder.name','data','syscheck','full_log'])
account=anyof(both(t('decoder.name','sudo'),t('data.srcuser','www-data')),both(t('decoder.name','useradd'),t('data.dstuser','backupsvc')),{'terms':{'syscheck.path':['/etc/passwd',cron]}})
add(4,'권한 요청과 계정 및 예약 파일 변경',[GOV,account],start='2026-09-29T02:00:00+09:00',end='2026-09-29T03:00:00+09:00',size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','decoder.name','rule.id','data','syscheck','full_log'])
shadow=both(GOV,t('decoder.name','auditd'),t('data.audit.command','cat /etc/shadow'))
ssh=both(t('decoder.name','sshd'),t('data.srcip','10.20.40.84'),{'terms':{'rule.id':['5715','5716']}})
add(5,'shadow 접근 명령과 서버발 SSH 순서',[anyof(shadow,ssh)],start='2026-10-12T03:00:00+09:00',end='2026-10-12T04:00:00+09:00',size=20,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','decoder.name','rule.id','data','full_log'])
v=terms('data.dest_ip',10);v['terms']['order']={'out_bytes':'desc'};v['aggs']={'out_bytes':m('sum','data.flow.bytes_toserver'),'sources':terms('data.src_ip',10),'first':m('min','timestamp'),'last':m('max','timestamp')}
add(6,'서버존의 실습망 밖 목적지별 전송',[FLOW,{'prefix':{'data.src_ip':'10.20.40.'}},{'bool':{'must_not':[{'prefix':{'data.dest_ip':'10.20.'}}]}}],{'destinations':v})
deleted=both(GOV,t('syscheck.event','deleted'),{'terms':{'syscheck.path':['/var/log/apache2/govportal_access.log','/root/.bash_history',shell]}})
add(7,'로그와 스크립트 삭제 원문',[deleted],start='2026-10-28T04:00:00+09:00',end='2026-10-28T05:00:00+09:00',size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','syscheck','full_log'])
# Observed in Q03's upload request under the fixed seed/anchor.
I2='60.173.18.44'
waf=both(t('decoder.name','modsecurity'),t('data.vhost','govportal.kt66.lab'),t('data.srcip',I1))
chain=anyof(both(GOV,{'terms':{'data.srcip':[I1,I2]}}),waf,both(GOV,t('data.audit.parent','/usr/sbin/apache2')),both(GOV,account,{'range':{'timestamp':{'gte':'2026-09-29T02:00:00+09:00','lt':'2026-09-29T03:00:00+09:00'}}}),both(GOV,t('syscheck.path',shell)),shadow,ssh,both(FLOW,t('data.src_ip','10.20.40.83'),t('data.dest_ip',I3)),deleted)
v={'date_histogram':{'field':'timestamp','calendar_interval':'day','time_zone':'+09:00','min_doc_count':1},'aggs':{'kinds':terms('decoder.name',20)}}
add(8,'확인한 단서로 날짜와 종류를 재구성',[chain],{'days':v})
add(9,'후보 전송의 원문 네 건',[FLOW,t('data.src_ip','10.20.40.83'),t('data.dest_ip',I3)],size=10,sort=[{'timestamp':'asc'}],_source=['timestamp','data'])
add(10,'WAF 센서에서 동일 가상 호스트의 차단 확인',[waf],size=2,sort=[{'timestamp':'asc'}],_source=['timestamp','agent.name','data','full_log'])
for n,q in Q.items():(OUT/f'Q03-09-{n}.http').write_text(q['method']+' '+q['path']+'\n'+json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'queries.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(len(Q),'queries; upload source',I2)
