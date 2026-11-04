"""Check one chapter artifact after Word rendering and individual page review."""
import argparse,hashlib,json,re,zipfile
from pathlib import Path
from lxml import etree as E
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',s)
def verify(chapter,pdf,reviewed):
    source=ROOT/f'manuscript/volume03-chapter{chapter:02}.json';doc=source.with_suffix('.docx')
    data=json.loads(source.read_text('utf8'));blocks=[b for p in data['pages'] for b in p['blocks']]
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(doc) as z,zipfile.ZipFile(ROOT/'tools/assets/bookk-B5.docx') as base:
        x=E.fromstring(z.read('word/document.xml'));y=E.fromstring(base.read('word/document.xml'))
        for k in ['pgSz','pgMar']:assert x.find('.//w:sectPr/w:'+k,ns).attrib==y.find('.//w:sectPr/w:'+k,ns).attrib
        assert z.read('word/theme/theme1.xml')==base.read('word/theme/theme1.xml')
        assert set(x.xpath('//w:color/@w:val',namespaces=ns))=={'000000'}
        text=''.join(x.xpath('//w:t/text()',namespaces=ns))
        media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
        images=[{'path':b['path'],'sha256':sha(ROOT/b['path'])} for b in blocks if b['type']=='image']
        assert all(i['sha256'] in media for i in images)
    reader=PdfReader(pdf);pdftext=norm(''.join(p.extract_text() for p in reader.pages))
    links=[b['url'] for b in blocks if b['type']=='link']
    for u in links:assert u in text and norm(u) in pdftext,u
    folder=ROOT/f'examples/chapter{chapter:02}';q=json.loads((folder/'queries.json').read_text('utf8')) if (folder/'queries.json').exists() else {}
    for n,r in q.items():
        lines=(folder/f'Q03-{chapter:02}-{n}.http').read_text('utf8').splitlines()
        assert lines[0]==r['method']+' '+r['path']
        assert (json.loads('\n'.join(lines[1:])) if r['body'] is not None else None)==r['body']
        matches=[b for b in blocks if b.get('id')==f'Q03-{chapter:02}-{n}']
        assert len(matches)==1,(n,'Missing or repeated printed query')
        lines2=matches[0]['text'].splitlines();assert lines2[0]==lines[0]
        assert (json.loads('\n'.join(lines2[1:])) if r['body'] is not None else None)==r['body']
    commands=[b for b in blocks if b['type']=='command'];shell=(folder/'commands.sh').read_text('utf8')
    assert all(b['text'] in shell for b in commands)
    assert not any(b['type']=='capture_slot' for b in blocks)
    result={'status':'pass','chapter':chapter,'pages':len(reader.pages),'individual_page_visual_review':reviewed,'page_geometry_and_theme_preserved':True,'text_black':True,'images':images,'urls_verified':links,'queries_match':len(q),'commands_match':len(commands),'files':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [doc,source]+list(folder.glob('*'))},'qa_pdf_published':False}
    (ROOT/f'editorial/chapter{chapter:02}-artifact-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print('PASS',len(reader.pages),'pages',len(images),'images',len(q),'queries','visual review',reviewed)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('chapter',type=int);p.add_argument('pdf',type=Path);p.add_argument('--reviewed-all-pages',action='store_true');a=p.parse_args();verify(a.chapter,a.pdf,a.reviewed_all_pages)
