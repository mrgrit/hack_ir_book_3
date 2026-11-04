"""Boundary checks for a packet reader and a create-only observation loader."""
import json,struct,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from inspect_pcap import inspect
from pcap_observations import prepare,check,upload
class PcapTests(unittest.TestCase):
 def test_capture_precision_and_truncation(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x.pcap';head=bytes.fromhex('4d3cb2a1')+struct.pack('<HHiIII',2,4,0,0,100,1)
   p.write_bytes(head+struct.pack('<IIII',10,123456789,4,8)+b'ABCD'+struct.pack('<IIII',11,0,4,4)+b'EFGH')
   m=inspect(p);self.assertEqual((m['packets'],m['truncated_packets'],m['captured_bytes']),(2,1,8));self.assertEqual(m['first_packet_utc'],'1970-01-01T00:00:10.123456789Z')
   p.write_bytes(p.read_bytes()[:-1])
   with self.assertRaises(ValueError):inspect(p)
 def test_pcapng_not_silently_read(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x';p.write_bytes(bytes.fromhex('0a0d0d0a')+b'\0'*20)
   with self.assertRaises(ValueError):inspect(p)
 def test_provenance_integrity_and_existing_index(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);(d/'meta').write_text(json.dumps({'sha256':'a'*64,'packets':1}));(d/'rules').write_text('rule');(d/'config').write_text('config')
   records=[{'timestamp':'2025-01-01T09:00:00.123456+0900','event_type':'http','flow_id':9007199254740993,'http':{'status':200}},{'timestamp':'2025-01-01T09:00:00+0900','event_type':'fileinfo'}]
   (d/'eve').write_text('\n'.join(json.dumps(x) for x in records)+'\n')
   a=SimpleNamespace(eve=d/'eve',pcap_info=d/'meta',rules=d/'rules',config=d/'config',run_id='test',sensor_version='test',out=d/'out');prepare(a);m=check(a.out);self.assertEqual(m['total'],1)
   doc=json.loads((a.out/'events.bulk.ndjson').read_text().splitlines()[1]);self.assertEqual(doc['data']['flow_id'],'9007199254740993');self.assertEqual(doc['timestamp'],'2025-01-01T00:00:00.123+00:00');self.assertNotIn('rule',doc)
   calls=[]
   def existing(method,path,*args):calls.append(method);return 200,{}
   with self.assertRaises(ValueError):upload(a.out,existing)
   self.assertEqual(calls,['HEAD'])
   with self.assertRaises(FileExistsError):prepare(a)
   with (a.out/'events.bulk.ndjson').open('a') as f:f.write('tamper\n')
   with self.assertRaises(ValueError):check(a.out)
if __name__=='__main__':unittest.main()
