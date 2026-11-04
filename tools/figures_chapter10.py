from figures import draw,ROOT
from PIL import Image
draw('chapter10-impact.png',[
 ('1  영향의 범위','파일 열람 · 업무 응답 · GPU 사용 상태'),
 ('2  같은 조건의 관측','호스트 · 경로 · 시간 · 요청 수 · 변경 종류'),
 ('3  원인 증거','내용·해시 · 프로세스 · 배포 승인 · 백엔드 상태'),
 ('4  대응과 복구 확인','증거 보존 · 확산 통제 · 복원 검사 · 업무 확인')],
 '대량 변경 · 웹 응답 변화 · 자원 사용을 독립된 근거로 조사한다')
Image.open(ROOT/'assets/screenshots/chapter10/fim-console.png').crop((750,205,1240,475)).save(ROOT/'assets/screenshots/chapter10/fim-detail.png')
