from figures import draw,ROOT
from PIL import Image
draw('chapter08-outbound-evidence.png',[
 ('1  통신의 주체와 대상','PC 주소 · 자산 소유 · 목적지 · 포트 · 프로세스'),
 ('2  시간과 이름의 분포','활동 날짜 · 개별 간격 · DNS 이름 · 질의 유형'),
 ('3  전송 방향과 내용','클라이언트→서버 바이트 · 파일 · 서비스 감사'),
 ('4  대응 후 확인','의심 통신 중단 · 수집 정상 · 승인 업무 복구')],
 '반복성·질의 이름·바이트 수는 조사 단서이며 내용 증거와 연결한다')
Image.open(ROOT/'assets/screenshots/chapter08/bytes-console.png').crop((750,150,1245,535)).save(ROOT/'assets/screenshots/chapter08/bytes-detail.png')
