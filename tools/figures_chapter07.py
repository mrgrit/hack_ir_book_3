from figures import draw,ROOT
from PIL import Image
draw('chapter07-connection-evidence.png',[
 ('1  접속 출발점','bastion 로그인 · 출발 IP · 승인된 원격 접속'),
 ('2  서버 접속 범위','kim.minjun · SSH 성공 6대 · dvwa 실패'),
 ('3  Windows 관측','neobank 출발 · park.jiwoo 로그온 · 프로세스'),
 ('4  계정 변경 이후','svc_backup 생성 · 그룹 추가 · 후속 로그온')],
 '계정 전환과 연결 식별자가 없는 구간은 추가 증거로 확인한다')
Image.open(ROOT/'assets/screenshots/chapter07/hosts-console.png').crop((750,140,1245,675)).save(ROOT/'assets/screenshots/chapter07/hosts-detail.png')
