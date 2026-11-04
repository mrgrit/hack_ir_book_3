from figures import draw,ROOT
from PIL import Image
draw('chapter05-gap-checks.png',[
 ('1  검색 범위 확인','인덱스 · 사건 시각 · 시간대 · 잔여 필터'),
 ('2  관측 출처 비교','해당 호스트 · 비교 호스트 · 네트워크 센서'),
 ('3  수집 경로 확인','로컬 파일 · 에이전트 · 전송 · 인덱싱'),
 ('4  공백 전후 조사','명령 · 파일 변경 · 승인된 유지보수')],
 '공백의 위치를 좁힌 뒤 원인과 대응을 기록한다')
Image.open(ROOT/'assets/screenshots/chapter05/gap-console.png').crop((755,180,1250,675)).save(ROOT/'assets/screenshots/chapter05/gap-detail.png')
