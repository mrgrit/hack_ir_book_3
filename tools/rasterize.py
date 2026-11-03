"""Rasterize QA-only PDF pages with the bundled Python runtime."""
import argparse
from pathlib import Path
from pdf2image import convert_from_path
ap=argparse.ArgumentParser();ap.add_argument('pdf',type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--dpi',type=int,default=120);ap.add_argument('--poppler');a=ap.parse_args()
a.out.mkdir(parents=True,exist_ok=True)
pages=convert_from_path(str(a.pdf),dpi=a.dpi,poppler_path=a.poppler)
for i,p in enumerate(pages,1):p.save(a.out/f'page-{i:02}.png')
print(f'{len(pages)} pages')
