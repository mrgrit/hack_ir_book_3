"""부크크 원본 DOCX에서 첫 구역의 판형·여백·테마를 상속하는 저자용 조판기."""
from illustration_assets import fit_existing_frame
import argparse
from illustration_assets import apply_extra_scenes
import json
from copy import deepcopy
from pathlib import Path
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(__file__).resolve().parents[1]
BODY='부크크 명조 Light'
HEAD='부크크 고딕 Light'
MONO='Consolas'

def font(r,name=BODY,size=10.5):
    r.font.name=name; r.font.size=Pt(size);r.font.color.rgb=RGBColor(0,0,0)
    rf=r._r.get_or_add_rPr().get_or_add_rFonts()
    for x in ['ascii','hAnsi','cs']:rf.set(qn('w:'+x),name)
    rf.set(qn('w:eastAsia'),BODY if name==MONO else name)
    return r

def runs(p,text,name,size):
    # **강조**는 제목·강조용 고딕으로 표시한다. 화면의 메뉴·버튼 이름에 쓴다.
    if '**' not in text or name==MONO:
        font(p.add_run(text),name,size);return
    for n,part in enumerate(text.split('**')):
        if part:font(p.add_run(part),HEAD if n%2 else name,size)

def para(parent,text='',size=10.5,name=BODY,after=6,keep=False,align=None,indent=0,hanging=0):
    p=parent.add_paragraph()
    pf=p.paragraph_format;pf.space_before=Pt(0);pf.space_after=Pt(after);pf.line_spacing=1.35
    pf.first_line_indent=Mm(-hanging);pf.left_indent=Mm(indent);pf.right_indent=Mm(0)
    pf.keep_with_next=keep;pf.keep_together=True;pf.widow_control=True
    p.alignment=align or WD_ALIGN_PARAGRAPH.LEFT
    snap=OxmlElement('w:snapToGrid');snap.set(qn('w:val'),'0');p._p.get_or_add_pPr().append(snap)
    runs(p,text,name,size)
    return p

def border(pr,tag='w:pBdr'):
    b=OxmlElement(tag)
    for side in ['top','left','bottom','right']:
        el=OxmlElement('w:'+side)
        for k,v in [('val','single'),('sz','4'),('space','0' if tag=='w:tcBorders' else '4'),('color','000000')]:el.set(qn('w:'+k),v)
        b.append(el)
    pr.append(b)

def table(doc,block):
    widths=block.get('widths') or [40,87]
    t=doc.add_table(rows=1,cols=len(block['head']));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.style='Normal Table'
    spacing=OxmlElement('w:tblCellSpacing');spacing.set(qn('w:w'),'0');spacing.set(qn('w:type'),'dxa')
    t._tbl.tblPr.append(spacing)
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        edge=OxmlElement('w:'+side)
        for key,value in [('val','single'),('sz','4'),('color','000000')]:edge.set(qn('w:'+key),value)
        borders.append(edge)
    t._tbl.tblPr.append(borders)
    for col,w in zip(t.columns,widths):col.width=Mm(w)
    for n,vals in enumerate([block['head']]+block['rows']):
        row=t.rows[0] if n==0 else t.add_row()
        trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
        if n==0:trpr.append(OxmlElement('w:tblHeader'))
        for cell,txt,w in zip(row.cells,vals,widths):
            cell.width=Mm(w);pr=cell._tc.get_or_add_tcPr()
            mar=OxmlElement('w:tcMar')
            for k,v in [('top',55),('bottom',55),('left',85),('right',85)]:
                e=OxmlElement('w:'+k);e.set(qn('w:w'),str(v));e.set(qn('w:type'),'dxa');mar.append(e)
            pr.append(mar)
            old=cell.paragraphs[0]
            cell._tc.remove(old._p)
            # 짧은 표는 한 쪽에 두고, 긴 표만 keep=False로 나눌 수 있다.
            para(cell,txt,size=10,name=HEAD if n==0 else BODY,after=0,keep=bool(block.get('keep',True)) and n<len(block['rows']))
    para(doc,'',size=1,after=3).paragraph_format.line_spacing=1

BOX_LABEL={'predict':'먼저 예측','caution':'주의','blind':'보이지 않는 것','field':'현장 노트','answer':'해설'}

def box(doc,block):
    """상자 4종: 먼저 예측·주의·보이지 않는 것·현장 노트. 한 칸 표로 만들어 한 쪽에 둔다."""
    t=doc.add_table(rows=1,cols=1);t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.columns[0].width=Mm(127)
    row=t.rows[0];row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    cell=t.cell(0,0);cell.width=Mm(127);pr=cell._tc.get_or_add_tcPr();border(pr,'w:tcBorders')
    mar=OxmlElement('w:tcMar')
    for k,v in [('top',90),('bottom',70),('left',140),('right',140)]:
        e=OxmlElement('w:'+k);e.set(qn('w:w'),str(v));e.set(qn('w:type'),'dxa');mar.append(e)
    pr.append(mar)
    cell._tc.remove(cell.paragraphs[0]._p)
    label=block.get('title') or BOX_LABEL[block['kind']]
    para(cell,label,name=HEAD,size=10,after=3,keep=True)
    texts=block['text'] if isinstance(block.get('text'),list) else ([block['text']] if block.get('text') else [])
    for n,txt in enumerate(texts):para(cell,txt,size=10,after=3 if n<len(texts)-1 or block.get('items') else 1)
    for n,item in enumerate(block.get('items',[])):
        para(cell,'• '+item,size=10,after=2,indent=4,hanging=4)
    para(doc,'',size=1,after=5).paragraph_format.line_spacing=1

def items(doc,block):
    numbered=block.get('style')=='number'
    for n,item in enumerate(block['items']):
        mark=f'{n+1}. ' if numbered else '• '
        # 네 항목 이하의 짧은 목록만 한 쪽에 묶는다. 긴 목록은 쪽 사이에서 나뉠 수 있다.
        para(doc,mark+item,after=3 if n<len(block['items'])-1 else 7,indent=5,hanging=5,keep=len(block['items'])<=4 and n<len(block['items'])-1)

def build(output,source=None):
    data=json.loads((source or ROOT/'manuscript/volume03-chapter01.json').read_text(encoding='utf-8'))
    apply_extra_scenes(data)
    doc=Document(ROOT/'tools/assets/bookk-B5.docx')
    sect=deepcopy(doc.sections[0]._sectPr)
    for x in list(doc.element.body):doc.element.body.remove(x)
    doc.element.body.append(sect)
    for tag in ['w:type','w:docGrid']:
        e=sect.find(qn(tag))
        if e is not None:sect.remove(e)
    # 테마와 판면은 보존하고 예시 본문·머리말 내용은 제거한다.
    s=doc.sections[0]
    for container in [s.header,s.even_page_header,s.first_page_header,s.footer,s.even_page_footer,s.first_page_footer]:
        for e in list(container._element):container._element.remove(e)
    for foot in [s.footer,s.even_page_footer]:
        p=para(foot,'',name=HEAD,size=9,align=WD_ALIGN_PARAGRAPH.CENTER)
        field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');p._p.append(field)
    normal=doc.styles['Normal'];normal.font.name=BODY;normal.font.size=Pt(10.5)
    normal.paragraph_format.space_after=Pt(6)
    for style_name in ['Title','Heading 1','Heading 2']:
        try:style=doc.styles[style_name]
        except KeyError:style=doc.styles.add_style(style_name,WD_STYLE_TYPE.PARAGRAPH)
        style.font.name=HEAD;style.font.color.rgb=RGBColor(0,0,0)
        for el in list(style.element.findall('.//'+qn('w:pBdr'))):el.getparent().remove(el)
    for idx,pg in enumerate(data['pages']):
        # break=False인 쪽은 앞 내용에 이어 조판한다. level=section은 절 제목 크기로 표시한다.
        brk=pg.get('break',True);section=pg.get('level')=='section'
        size=25 if pg['kind']=='cover' else (13.5 if section else 16)
        title=para(doc,pg['title'],size=size,name=HEAD,after=8 if section else 13,keep=True)
        title.style=doc.styles['Title' if idx==0 else 'Heading 1']
        title.paragraph_format.page_break_before=idx>0 and brk
        if idx>0 and not brk:title.paragraph_format.space_before=Pt(14)
        if section and not brk:title.paragraph_format.space_before=Pt(14)
        if pg['kind']=='cover':
            title.paragraph_format.space_before=Pt(120)
            title.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for b in pg['blocks']:
            typ=b['type']
            if typ=='p':para(doc,b['text'],align=WD_ALIGN_PARAGRAPH.CENTER if pg['kind']=='cover' else None)
            elif typ=='h':para(doc,b['text'],size=11.5,name=HEAD,after=5,keep=True)
            elif typ in ('command','query') and 'purpose' in b:
                # 번호·위치 → 목적 → 입력 → 구문 → 확인. 한 블록은 같은 쪽에 둔다.
                para(doc,b['id']+'  |  '+b['where'],size=9,name=HEAD,after=2,keep=True)
                para(doc,'**목적**  '+b['purpose'],after=3,keep=True)
                p=para(doc,b['text'],size=10,name=MONO,after=4,keep=True)
                p.paragraph_format.line_spacing=1.15
                if b.get('long'):
                    p.paragraph_format.keep_together=False
                    p.paragraph_format.keep_with_next=False
                border(p._p.get_or_add_pPr())
                if b.get('syntax'):para(doc,'**구문**  '+b['syntax'],after=3,keep=True)
                para(doc,'**확인**  '+b['result'],after=9)
            elif typ in ('command','query'):
                para(doc,b['id']+'  |  '+b['where'],size=9,name=HEAD,after=2,keep=True)
                # 역할·기호 → 입력 → 판정 순서. 한 명령 블록은 같은 쪽에 둔다.
                para(doc,b['why'],after=3,keep=True)
                p=para(doc,b['text'],size=10,name=MONO,after=4,keep=True)
                p.paragraph_format.line_spacing=1.15
                border(p._p.get_or_add_pPr())
                para(doc,'확인  '+b['result'],after=9)
            elif typ=='code':
                p=para(doc,b['text'],name=MONO,size=10,after=6)
                if b.get('long'):p.paragraph_format.keep_together=False
            elif typ=='table':table(doc,b)
            elif typ=='box':box(doc,b)
            elif typ=='list':items(doc,b)
            elif typ=='image':
                p=para(doc,'',after=3,keep=True,align=WD_ALIGN_PARAGRAPH.RIGHT if b.get('align')=='right' else WD_ALIGN_PARAGRAPH.CENTER)
                p.paragraph_format.line_spacing=1
                shape=p.add_run().add_picture(str(ROOT/b['path']),width=Mm(b.get('width_mm',127)))
                shape._inline.docPr.set('descr',b['caption'])
                fit_existing_frame(shape,b['path'])
                para(doc,b['caption'],size=9,after=7,align=WD_ALIGN_PARAGRAPH.RIGHT if b.get('align')=='right' else None)
            elif typ=='capture_slot':
                t=doc.add_table(rows=1,cols=1);t.autofit=False;t.columns[0].width=Mm(127)
                cell=t.cell(0,0);cell.width=Mm(127);border(cell._tc.get_or_add_tcPr(),'w:tcBorders')
                cell._tc.remove(cell.paragraphs[0]._p)
                para(cell,b['title'],name=HEAD,size=10,after=4)
                para(cell,b['text'],size=9.5,after=4)
                para(doc,'',size=1,after=3)
            elif typ=='link':
                p=para(doc,'',size=10,after=b.get('title_after',7))
                link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to(b['url'],RT.HYPERLINK,is_external=True))
                r=font(p.add_run(b['text']),BODY,10);p._p.remove(r._r);link.append(r._r);p._p.append(link)
                p.paragraph_format.keep_with_next=True
                urlpara=para(doc,'',name=MONO,size=10,after=b.get('url_after',9))
                url_link=OxmlElement('w:hyperlink');url_link.set(qn('r:id'),p.part.relate_to(b['url'],RT.HYPERLINK,is_external=True))
                r=font(urlpara.add_run(b['url']),MONO,10);urlpara._p.remove(r._r);url_link.append(r._r);urlpara._p.append(url_link)
            else:raise ValueError(typ)
    doc.core_properties.title=data['title'];doc.core_properties.subject=data['series'];doc.core_properties.language='ko-KR'
    doc.core_properties.author='';doc.core_properties.comments=data.get('comments','신규 원고. 설치 절차는 문서·코드 대조 상태. 실제 UI는 기존 가동 환경에서 촬영.')
    output.parent.mkdir(parents=True,exist_ok=True);doc.save(output)
    print(output)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'build/volume03-chapter01.docx')
    ap.add_argument('--source',type=Path)
    args=ap.parse_args();build(args.output,args.source)
