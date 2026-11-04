"""삽화 자산과 추가 장면을 조판에 공통 적용한다. 래스터 파일은 변형하지 않는다."""
import json
from pathlib import Path
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
_manifest=ROOT/'editorial/illustration-refresh.json'
SCENES=json.loads(_manifest.read_text('utf8'))['scenes'] if _manifest.exists() else []

def resolve_path(chapter,path):
    return next((s['path'] for s in SCENES if s.get('chapter')==chapter and s.get('old')==path),path)

def fit_existing_frame(shape,path):
    """기존 지면 크기를 유지하고 가로·세로 여백으로 새 원본 비율을 보존한다."""
    rec=next((s for s in SCENES if s['path']==path and 'frame_size' in s),None)
    if not rec:return
    oldw,oldh=rec['frame_size'];nw,nh=rec['image_size']
    shape.height=round(shape.width*oldh/oldw)
    rect=shape._inline.find('.//'+qn('a:fillRect'))
    rect.attrib.clear()
    frame_ratio=oldw/oldh;image_ratio=nw/nh
    if image_ratio>frame_ratio:
        margin=round((1-frame_ratio/image_ratio)*50000)
        if margin:rect.set('t',str(margin));rect.set('b',str(margin))
    else:
        margin=round((1-image_ratio/frame_ratio)*50000)
        if margin:rect.set('l',str(margin));rect.set('r',str(margin))

def apply_extra_scenes(data):
    """저자용 목록의 본문 위치에 추가 삽화를 넣는다. 이미 있는 장면은 중복하지 않는다."""
    path=ROOT/'editorial/additional-black-scenes.json'
    if not path.exists():return data
    for scene in json.loads(path.read_text('utf8'))['scenes']:
        if any(b.get('path')==scene['asset'] for pg in data['pages'] for b in pg['blocks']):continue
        matches=[(pg,i) for pg in data['pages'] for i,b in enumerate(pg['blocks'])
                 if b.get('type')=='p' and any(b.get('text','').startswith(a) for a in scene['anchors'])]
        if not matches:continue
        if len(matches)!=1:raise ValueError('추가 삽화 위치가 유일하지 않음: '+scene['id'])
        pg,i=matches[0]
        pg['blocks'].insert(i+1,{'type':'image','path':scene['asset'],'caption':scene['caption'],
                                'width_mm':scene['width_mm'],'align':'right'})
    return data
