from figures import draw,ROOT
from PIL import Image
draw('chapter09-evidence-chain.png',[
 ('1  웹 요청과 센서','외부 IP · vhost · 응답 변화 · WAF 관측'),
 ('2  호스트 변경','파일 생성 · apache2 자식 셸 · sudo · 계정 · cron'),
 ('3  서버 사이의 접근','govportal 출발 · deploy 인증 · neobank·mediforum'),
 ('4  후속 범위와 보존','neobank 외향 전송 · govportal 삭제 · 추가 증거')],
 '시간순 연결과 같은 행위자·자격증명·파일 내용의 입증을 구분한다')
Image.open(ROOT/'assets/screenshots/chapter09/timeline-console.png').crop((750,174,1245,680)).save(ROOT/'assets/screenshots/chapter09/timeline-detail.png')
