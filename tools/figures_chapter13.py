from figures import draw,ROOT
from PIL import Image
draw('chapter13-decisions.png',[
 ('1  조사 대상을 분리한다','PC 장기 활동 / AI 서비스 활동 / 승인 작업'),
 ('2  원문과 연결 근거를 적는다','시각 · 호스트 · 계정 · 요청 · 세션 · 파일'),
 ('3  승인 범위와 영향을 대조한다','담당자 · 기간 · 대상 · 작업 내용 · 예외'),
 ('4  조치와 종료 조건을 정한다','보존 · 제한 · 정상 업무 시험 · 재발 감시')],
 '조사표에서 사실 · 추론 · 미확인 · 모의 조치를 구분한다')
Image.open(ROOT/'assets/screenshots/chapter13/export-console.png').crop((705,303,1255,708)).save(ROOT/'assets/screenshots/chapter13/export-detail.png')
