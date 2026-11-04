from figures import draw,ROOT
from PIL import Image
draw('chapter04-evidence-chain.png',[
 ('요청 · 웹 접근 기록','출발지 · 서비스 · 경로 · 응답 · 사건 시각'),
 ('파일 · 무결성 감시','같은 호스트의 업로드 경로와 추가 시각'),
 ('실행 · 감사 기록','부모 프로세스 · 실행 파일 · 명령 · 사용자'),
 ('지속성 · 후속 기록','계정 · 예약 작업 · 키 파일 · 반복 실행')],
 'R04 안에서 호스트 · 경로 · 시각으로 연결한다')
Image.open(ROOT/'assets/screenshots/chapter04/extensions-console.png').crop((700,395,1020,698)).save(ROOT/'assets/screenshots/chapter04/extensions-detail.png')
