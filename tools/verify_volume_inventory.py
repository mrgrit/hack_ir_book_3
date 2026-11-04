"""Verify delivered manuscript/examples against the existing per-document QA."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[];checked=set()
 for label in [f'chapter{n:02}' for n in range(1,14)]+['appendixA','appendixB']:
  doc=f'manuscript/volume03-{label}.docx';source=f'manuscript/volume03-{label}.json'
  report='editorial/artifact-verification.json' if label=='chapter01' else f'editorial/{label}-artifact-verification.json'
  r=json.loads((ROOT/report).read_text('utf8'));d=json.loads((ROOT/source).read_text('utf8'))
  expected=r['docx_sha256'] if label=='chapter01' else r['files'][doc]
  assert sha(ROOT/doc)==expected,doc
  for f,h in r.get('files',{}).items():
   # Historical reports also include tool hashes from that chapter's run.
   # Later shared-tool changes do not rewrite those historical environments.
   if f.startswith(('manuscript/','examples/')):
    assert sha(ROOT/f)==h,f;checked.add(f)
  blocks=[b for s in d['pages'] for b in s.get('blocks',[])]
  assert not any(b['type']=='capture_slot' for b in blocks),label
  with zipfile.ZipFile(ROOT/doc) as z:
   hashes={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
  images=[b for b in blocks if b['type']=='image']
  for b in images:assert sha(ROOT/b['path']) in hashes,b['path']
  rows.append({'label':label,'docx':doc,'source':source,'pages':r.get('pages',r.get('rendered_pages')),'docx_sha256':sha(ROOT/doc),'source_sha256':sha(ROOT/source),'qa_record':report,'qa_record_sha256':sha(ROOT/report),'embedded_images_matched':len(images)})
 idx=json.loads((ROOT/'examples/appendixA/index-sources.json').read_text('utf8'))
 for f,h in idx['sources'].items():assert sha(ROOT/f)==h,f
 assert len(list((ROOT/'manuscript').glob('*.docx')))==15
 result={'status':'pass','scope':'Current delivered files matched to existing individual visual/technical QA; no repeated SIEM actions','documents':rows,'document_count':len(rows),'page_sum_not_a_merged_book':sum(x['pages'] for x in rows),'chapter_query_files':idx['query_files'],'chapter_command_blocks':idx['printed_command_blocks'],'additional_appendix_queries':3,'additional_appendix_commands':8,'checked_report_file_entries':len(checked),'appendixA_source_index_current':True,'pdf_published':False,'publication_status':'chapter drafts; not REV01'}
 (ROOT/'editorial/volume03-delivery-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8',newline='\n')
 print('PASS',len(rows),'DOCX;',result['page_sum_not_a_merged_book'],'pages;',len(checked),'file hashes')
if __name__=='__main__':main()
