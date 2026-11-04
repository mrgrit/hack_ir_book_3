from figures import draw,ROOT
from PIL import Image
if __name__=='__main__':
    draw('chapter03-axis.png',[('출발지 → 경로','한 주소가 얼마나 넓게 탐색했는가'),('경로 → 출발지','같은 경로에 얼마나 많은 주소가 모였는가'),('날짜 → 원문','집중 활동과 낮은 빈도 재방문을 구분한다')],'서비스 · 응답 · 기간을 고정한 뒤 묶음의 축을 바꾼다')
    Image.open(ROOT/'assets/screenshots/chapter03/paths-console.png').crop((700,334,1170,696)).save(ROOT/'assets/screenshots/chapter03/paths-detail.png')
