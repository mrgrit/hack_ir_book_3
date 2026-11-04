"""Shared authoring components. Creates only the explicitly requested chapter."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def p(t):return {'type':'p','text':t}
def h(t):return {'type':'h','text':t}
def tab(head,rows,widths,keep=True):return {'type':'table','head':head,'rows':rows,'widths':widths,'keep':keep}
def pic(path,caption,width=121):return {'type':'image','path':path,'caption':caption,'width_mm':width}
def code(t):return {'type':'code','text':t,'long':True}
def steps(*items):return {'type':'list','style':'number','items':list(items)}
def link(t,u):return {'type':'link','text':t,'url':u}
def compact(value,indent=0,prefix_length=0):
    one=json.dumps(value,ensure_ascii=False,separators=(', ',': '))
    if len(one)+indent+prefix_length<=64:return one
    if isinstance(value,dict):return '{\n'+',\n'.join(' '*(indent+2)+json.dumps(k)+': '+compact(v,indent+2,len(k)+4) for k,v in value.items())+'\n'+' '*indent+'}'
    if isinstance(value,list):return '[\n'+',\n'.join(' '*(indent+2)+compact(x,indent+2) for x in value)+'\n'+' '*indent+']'
    return one
class Book:
    def __init__(self,chapter,title):
        self.chapter=chapter;self.title=title;self.pages=[];self.commands=[]
        self.folder=ROOT/f'examples/chapter{chapter:02}'
        self.queries=json.loads((self.folder/'queries.json').read_text('utf8')) if (self.folder/'queries.json').exists() else {}
    def section(self,title,*blocks):
        self.pages.append({'kind':'content','title':title,'blocks':list(blocks),'break':not self.pages,'level':'chapter' if not self.pages else 'section'})
    def cmd(self,n,text,purpose,syntax,result,where='kt66 Ubuntu VM의 호스트 터미널'):
        b={'type':'command','id':f'C03-{self.chapter:02}-{n:02}','where':where,'text':text,'purpose':purpose,'syntax':syntax,'result':result};self.commands.append(b);return b
    def query(self,n,purpose,syntax,result):
        q=self.queries[f'{n:02}'];t=q['method']+' '+q['path']
        if q['body'] is not None:t+='\n'+compact(q['body'])
        return {'type':'query','id':f'Q03-{self.chapter:02}-{n:02}','where':'Windows 브라우저 · Wazuh Dev Tools','text':t,'purpose':purpose,'syntax':syntax,'result':result,'long':True}
    def write(self,comments,indices=(),dql=(),preamble=()):
        target=ROOT/f'manuscript/volume03-chapter{self.chapter:02}.json'
        target.write_text(json.dumps({'title':self.title,'series':'해킹·침해대응 실무 with Wazuh — 3권','comments':comments,'pages':self.pages},ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        self.folder.mkdir(parents=True,exist_ok=True)
        (self.folder/'commands.sh').write_text('#!/usr/bin/env bash\n# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.\n\n'+'\n\n'.join(preamble)+('\n\n' if preamble else '')+'\n\n'.join('# '+b['id']+' '+b['purpose']+'\n'+b['text'] for b in self.commands)+'\n',encoding='utf8',newline='\n')
        (self.folder/'discover.dql').write_text('# 각 검색식을 따로 입력한다.\n'+'\n\n'.join(dql)+'\n',encoding='utf8',newline='\n')
        cleanup=[]
        for index in indices:cleanup.extend(['# 원고의 소유 정보·해시·백업 확인 후 제거가 필요할 때만 실행',f'GET /{index}/_mapping',f'DELETE /{index}',f'GET /{index}/_count'])
        (self.folder/'cleanup.http').write_text('\n\n'.join(cleanup)+'\n',encoding='utf8',newline='\n')
        with (self.folder/'investigation.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(['항목','기록']);w.writerows((x,'') for x in ['인덱스와 manifest 해시','기간과 시간대','조회 파일','관찰 대상과 연결 필드','원문 이벤트 _id','비교 기준과 정상 작업','관찰한 사실','추가 확보할 증거','대응과 성공 기준','원상복구 기록'])
        print(target,len(self.pages),'sections')
