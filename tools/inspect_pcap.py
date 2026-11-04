"""Read classic PCAP metadata without decoding, extracting or transmitting payload."""
import argparse,hashlib,json,struct
from datetime import datetime,timezone
from pathlib import Path

def inspect(path):
    magic={b'\xd4\xc3\xb2\xa1':('<',1000000),b'\xa1\xb2\xc3\xd4':('>',1000000),b'\x4d\x3c\xb2\xa1':('<',1000000000),b'\xa1\xb2\x3c\x4d':('>',1000000000)}
    h=hashlib.sha256();count=truncated=stored=wire=inversions=0;first=last=prev=None
    with path.open('rb') as f:
        header=f.read(24);h.update(header)
        if len(header)!=24 or header[:4] not in magic:raise ValueError('Only classic PCAP is supported; use capinfos for PCAPNG')
        endian,unit=magic[header[:4]];major,minor,zone,sig,snap,link=struct.unpack(endian+'HHiIII',header[4:])
        if (major,minor)!=(2,4):raise ValueError('Unsupported PCAP version')
        while True:
            record=f.read(16)
            if not record:break
            if len(record)!=16:raise ValueError('Truncated packet header')
            h.update(record);sec,fraction,inc,orig=struct.unpack(endian+'IIII',record)
            if fraction>=unit or inc>orig or inc>snap or inc>16*1024*1024:raise ValueError('Invalid packet header')
            packet=f.read(inc)
            if len(packet)!=inc:raise ValueError('Truncated packet data')
            h.update(packet);tick=sec*unit+fraction
            inversions+=int(prev is not None and tick<prev);prev=tick
            first=tick if first is None else min(first,tick);last=tick if last is None else max(last,tick)
            count+=1;truncated+=int(inc<orig);stored+=inc;wire+=orig
    def iso(t):
        if t is None:return None
        return datetime.fromtimestamp(t//unit,timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')+'.'+str(t%unit).zfill(6 if unit==1000000 else 9)+'Z'
    return {'schema_version':1,'format':'classic-pcap','bytes':path.stat().st_size,'sha256':h.hexdigest(),'version':f'{major}.{minor}','timestamp_precision':'microsecond' if unit==1000000 else 'nanosecond','link_type':link,'snaplen':snap,'packets':count,'captured_bytes':stored,'original_bytes':wire,'truncated_packets':truncated,'time_inversions':inversions,'first_packet_utc':iso(first),'last_packet_utc':iso(last),'duration_seconds':(last-first)/unit if first is not None else 0,'payload_extracted':False,'packets_transmitted':0}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pcap',type=Path);a=p.parse_args();print(json.dumps(inspect(a.pcap),indent=2))
