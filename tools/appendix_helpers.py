"""Appendix authoring shares the chapter renderer, not the chapter numbering."""
from chapter_helpers import *
class Appendix:
 def __init__(self,letter,title):self.letter=letter;self.title=title;self.pages=[];self.commands=[];self.queries={};self.folder=ROOT/f'examples/appendix{letter}';self.folder.mkdir(parents=True,exist_ok=True)
 def section(self,title,*blocks):self.pages.append({'kind':'content','title':title,'blocks':list(blocks),'break':not self.pages,'level':'chapter' if not self.pages else 'section'})
 def cmd(self,n,text,purpose,syntax,result,where='kt66 Ubuntu VM 호스트 · 3권 저장소 루트'):
  b={'type':'command','id':f'C03-{self.letter}-{n:02}','where':where,'text':text,'purpose':purpose,'syntax':syntax,'result':result};self.commands.append(b);return b
 def query(self,n,request,purpose,syntax,result):
  lines=request.splitlines();method,path=lines[0].split(' ',1);body=json.loads('\n'.join(lines[1:])) if len(lines)>1 else None
  self.queries[f'{n:02}']={'title':purpose,'method':method,'path':path,'body':body}
  return {'type':'query','id':f'Q03-{self.letter}-{n:02}','where':'Windows 브라우저 · Wazuh Dev Tools','text':request,'purpose':purpose,'syntax':syntax,'result':result,'long':True}
 def write(self,comments):
  (ROOT/f'manuscript/volume03-appendix{self.letter}.json').write_text(json.dumps({'title':self.title,'series':'해킹·침해대응 실무 with Wazuh — 3권','comments':comments,'pages':self.pages},ensure_ascii=False,indent=2)+'\n','utf8',newline='\n')
  (self.folder/'commands.sh').write_text('#!/usr/bin/env bash\n# 본문의 실행 위치에서 한 명령씩 입력한다.\n\n'+'\n\n'.join('# '+x['id']+' '+x['purpose']+'\n'+x['text'] for x in self.commands)+'\n','utf8',newline='\n')
  (self.folder/'queries.json').write_text(json.dumps(self.queries,ensure_ascii=False,indent=2)+'\n','utf8',newline='\n')
  for n,q in self.queries.items():(self.folder/f'Q03-{self.letter}-{n}.http').write_text(q['method']+' '+q['path']+'\n'+(json.dumps(q['body'],ensure_ascii=False,indent=2)+'\n' if q['body'] is not None else ''),'utf8',newline='\n')
  print('appendix',self.letter,len(self.pages),'sections')
