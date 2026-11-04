"""Verify one appendix, source indexes, example consistency and reviewed layout."""
import argparse,csv,json,zipfile
from pathlib import Path
from lxml import etree as E
from pypdf import PdfReader
from verify_artifact import ROOT,sha,norm

def verify(letter,pdf,reviewed):
 source=ROOT/f'manuscript/volume03-appendix{letter}.json';doc=source.with_suffix('.docx');data=json.loads(source.read_text('utf8'));blocks=[b for s in data['pages'] for b in s['blocks']];ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 with zipfile.ZipFile(doc) as z,zipfile.ZipFile(ROOT/'tools/assets/bookk-B5.docx') as base:
  x=E.fromstring(z.read('word/document.xml'));y=E.fromstring(base.read('word/document.xml'))
  for k in ['pgSz','pgMar']:assert x.find('.//w:sectPr/w:'+k,ns).attrib==y.find('.//w:sectPr/w:'+k,ns).attrib
  assert z.read('word/theme/theme1.xml')==base.read('word/theme/theme1.xml')
  assert set(x.xpath('//w:color/@w:val',namespaces=ns))=={'000000'}
  fonts=set(x.xpath('//w:rFonts/@w:ascii',namespaces=ns));assert {'부크크 명조 Light','부크크 고딕 Light','Consolas'}<=fonts,fonts
  text=''.join(x.xpath('//w:t/text()',namespaces=ns));media={sha_bytes(z.read(n)) for n in z.namelist() if n.startswith('word/media/')}
  images=[{'path':b['path'],'sha256':sha(ROOT/b['path'])} for b in blocks if b['type']=='image'];assert all(i['sha256'] in media for i in images)
 reader=PdfReader(pdf);pdftext=norm(''.join(p.extract_text() for p in reader.pages));urls=[b['url'] for b in blocks if b['type']=='link']
 for u in urls:assert u in text and norm(u) in pdftext,u
 folder=ROOT/f'examples/appendix{letter}';queries=json.loads((folder/'queries.json').read_text('utf8'))
 for n,q in queries.items():
  lines=(folder/f'Q03-{letter}-{n}.http').read_text('utf8').splitlines();assert lines[0]==q['method']+' '+q['path'];assert (json.loads('\n'.join(lines[1:])) if q['body'] is not None else None)==q['body']
  b=[b for b in blocks if b.get('id')==f'Q03-{letter}-{n}'];assert len(b)==1;assert b[0]['text'].splitlines()[0]==lines[0]
  assert (json.loads('\n'.join(b[0]['text'].splitlines()[1:])) if q['body'] is not None else None)==q['body']
 commands=[b for b in blocks if b['type']=='command'];shell=(folder/'commands.sh').read_text('utf8');assert all(b['text'] in shell for b in commands)
 assert not any(b['type']=='capture_slot' for b in blocks)
 if letter=='A':
  idx=json.loads((folder/'index-sources.json').read_text('utf8'))
  for path,digest in idx['sources'].items():assert sha(ROOT/path)==digest,path
  for filename,count in [('query-index.csv',idx['query_files']),('command-index.csv',idx['printed_command_blocks'])]:
   with (folder/filename).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
   assert len(rows)==count;assert len({r['ID'] for r in rows})==count
   for r in rows:assert (ROOT/r['파일']).exists(),r
 result={'status':'pass','appendix':letter,'pages':len(reader.pages),'individual_page_visual_review':reviewed,'page_geometry_and_theme_preserved':True,'text_black':True,'fonts':sorted(fonts),'images':images,'urls_verified':urls,'queries_match':len(queries),'commands_match':len(commands),'files':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [doc,source]+list(folder.glob('*')) if p.is_file()},'qa_pdf_published':False}
 (ROOT/f'editorial/appendix{letter}-artifact-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print('PASS',letter,len(reader.pages),'pages; visual review',reviewed)
def sha_bytes(b):
 import hashlib
 return hashlib.sha256(b).hexdigest()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('letter',choices=['A','B']);p.add_argument('pdf',type=Path);p.add_argument('--reviewed-all-pages',action='store_true');a=p.parse_args();verify(a.letter,a.pdf,a.reviewed_all_pages)
