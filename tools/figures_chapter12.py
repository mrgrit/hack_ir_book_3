from figures import draw,ROOT
from PIL import Image
draw('chapter12-observation.png',[
 ('1  원본 캡처 보존','출처 · SHA-256 · 패킷 시각 · 절단 여부'),
 ('2  센서가 파일 읽기','Suricata EVE · Zeek HTTP / 연결 로그'),
 ('3  두 경로로 확인','logtest의 규칙 분류 · 전용 인덱스 집계'),
 ('4  원본으로 돌아가기','PCAP 해시 · 패킷 번호 · flow_id / uid')],
 '관측 문서 수 · 요청 수 · 경보 수의 단위를 구분한다')
draw('chapter12-replay.png',[
 ('송신 네임스페이스 b3-tx','tcpreplay · veth 송신 끝 · 원래 패킷 간격'),
 ('수신 네임스페이스 b3-rx','veth 수신 끝 · Suricata · 새 관측 시각'),
 ('출력 파일의 수집과 비교','원래 시각 · 재생 속도 · 수신 패킷 · 센서 손실')],
 '물리 NIC · 브리지 · IP 주소 · 기본 경로를 연결하지 않는다')
Image.open(ROOT/'assets/screenshots/chapter12/pcap-console.png').crop((695,300,1254,708)).save(ROOT/'assets/screenshots/chapter12/pcap-detail.png')
