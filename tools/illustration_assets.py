"""삽화 교체표를 원고 생성과 조판에 공통 적용한다. 래스터 파일은 변형하지 않는다."""
import json
from pathlib import Path
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
_manifest=ROOT/'editorial/illustration-refresh.json'
SCENES=json.loads(_manifest.read_text('utf8'))['scenes'] if _manifest.exists() else []

def resolve_path(chapter,path):
    return next((s['path'] for s in SCENES if s.get('chapter')==chapter and s.get('old')==path),path)

def fit_existing_frame(shape,path):
    """기존 삽화의 지면 높이를 유지하고 새 그림을 비율대로 중앙 배치한다."""
    rec=next((s for s in SCENES if s['path']==path and 'frame_size' in s),None)
    if not rec:return
    oldw,oldh=rec['frame_size'];nw,nh=rec['image_size']
    shape.height=round(shape.width*oldh/oldw)
    margin=round((1-nh/nw*oldw/oldh)/2*100000)
    rect=shape._inline.find('.//'+qn('a:fillRect'))
    rect.set('t',str(margin));rect.set('b',str(margin))
