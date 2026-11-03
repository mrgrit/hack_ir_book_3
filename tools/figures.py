"""Generate relationship diagrams only; never simulated application screens."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
FONT=Path('C:/Users/Student/AppData/Local/Microsoft/Windows/Fonts/BookkGothic_Light.ttf')
if not FONT.exists():FONT=Path('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')

def draw(name,labels,footer):
    w=1500;h=160+len(labels)*245
    im=Image.new('RGB',(w,h),'white');d=ImageDraw.Draw(im)
    f=ImageFont.truetype(str(FONT),48);s=ImageFont.truetype(str(FONT),38)
    for i,(title,body) in enumerate(labels):
        y=35+i*245
        d.rectangle((45,y,w-45,y+185),fill='#f5f0df',outline='#263a45',width=5)
        d.rectangle((45,y,68,y+185),fill='#477a80')
        d.text((100,y+24),title,font=f,fill='#152a35')
        d.text((100,y+100),body,font=s,fill='#152a35')
        if i<len(labels)-1:
            d.line((w//2,y+190,w//2,y+226),fill='#263a45',width=8)
            d.polygon(((w//2-16,y+215),(w//2+16,y+215),(w//2,y+234)),fill='#263a45')
    d.text((45,h-85),footer,font=s,fill='#152a35')
    dest=ROOT/'assets/figures'/name;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)

def paths():
    im=Image.new('RGB',(1500,1050),'white');d=ImageDraw.Draw(im)
    f=ImageFont.truetype(str(FONT),48);s=ImageFont.truetype(str(FONT),37)
    rows=[('생성 로그','생성기 → 전용 인덱스','검색과 집계의 판단 연습'),('원문 로그','원문 → Wazuh manager','디코더와 규칙의 실제 결과'),('캡처 패킷','PCAP → 센서 → 원문 로그','패킷에서 관측한 통신 기록')]
    for i,(a,b,c) in enumerate(rows):
        y=35+i*320
        d.rectangle((45,y,1455,y+270),fill='#f5f0df',outline='#263a45',width=5)
        d.text((88,y+25),a,font=f,fill='#152a35');d.text((88,y+104),b,font=f,fill='#152a35');d.text((88,y+191),c,font=s,fill='#152a35')
    dest=ROOT/'assets/figures/evidence-paths.png';dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)

if __name__=='__main__':
    paths()
    draw('three-times.png',[('사건 시각','기록에 표현된 동작의 시각'),('센서 관측 시각','센서가 패킷이나 동작을 본 시각'),('수집 도착 시각','manager가 기록을 받은 시각')],'동일 사건에서도 세 시각은 다를 수 있다')
    draw('preparation-flow.png',[('1  버전과 기간 고정','코드 커밋 · 기준일 · 90일 · 규모 배율'),('2  로컬 파일 생성','이벤트 · 별도 정답 · manifest'),('3  파일 검사','해시 · 건수 · 시각 범위 · 전체 순서'),('4  분석에 인계','데이터 이름 · 범위 · 검증 기록')],'적재 전까지 원문과 정답을 별도로 유지한다')
