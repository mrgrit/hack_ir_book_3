from figures import draw,ROOT
from PIL import Image
draw('chapter11-evidence.png',[
 ('1  사용자 입력과 외부 자료','계정 · 요청 · 문서 출처 · 입력 표지'),
 ('2  도구 요청과 권한 결정','요청 ID · 도구 · 인수 · 실행 주체 · 승인'),
 ('3  실제 후속 동작','프로세스 · 파일 접근 · 내부 HTTP · 결과'),
 ('4  영향과 통제 확인','전달 내용 · 허용 범위 · 재시험 · 정상 업무')],
 '입력 표지와 도구 이름을 실제 실행 결과에 연결한다')
Image.open(ROOT/'assets/screenshots/chapter11/ai-console.png').crop((755,180,1235,655)).save(ROOT/'assets/screenshots/chapter11/ai-detail.png')
