"""Verify a known archive and write only its declared PCAP member to a new file."""
import argparse,getpass,hashlib,json,zipfile
from pathlib import Path
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive',type=Path);p.add_argument('output',type=Path);p.add_argument('--manifest',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise FileExistsError(a.output)
 m=json.loads(a.manifest.read_text('utf8'))
 if hashlib.sha256(a.archive.read_bytes()).hexdigest()!=m['zip_sha256']:raise ValueError('Archive hash differs')
 with zipfile.ZipFile(a.archive) as z:
  items=z.infolist()
  if len(items)!=1 or items[0].filename!=m['member'] or items[0].file_size!=m['pcap_bytes']:raise ValueError('Unexpected archive member')
  data=z.read(items[0],pwd=getpass.getpass('Archive password from provider: ').encode())
 if hashlib.sha256(data).hexdigest()!=m['pcap_sha256']:raise ValueError('PCAP hash differs')
 with a.output.open('xb') as f:f.write(data)
 print('Verified PCAP:',len(data),'bytes; no files executed')
