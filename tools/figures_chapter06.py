from figures import draw,ROOT
from PIL import Image
draw('chapter06-evidence-links.png',[
 ('1  계정 후보','실패 출발지 분포 · 성공 출발지 · 승인된 접속'),
 ('2  메일 수신','발신 도메인 · 수신자 · 전달 시각'),
 ('3  로그인 후 요청','같은 출발지 · 시간 · 메일 표시 경로'),
 ('4  추가 증거와 조치','세션 식별자 · 원본 메일 · 사용자 확인')],
 '수신·로그인·표시 요청 사이의 관찰과 가설을 구분한다')
Image.open(ROOT/'assets/screenshots/chapter06/mail-console.png').crop((740,165,1245,633)).save(ROOT/'assets/screenshots/chapter06/mail-detail.png')
