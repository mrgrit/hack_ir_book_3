"""Code-native relationship diagrams; screenshot crops preserve captured pixels."""
from figures import draw,FONT,ROOT
from PIL import Image,ImageDraw,ImageFont

def build():
    draw('chapter02-aggregation-flow.png',[
        ('1  선택 · query','인덱스 · 기간 · 로그 종류를 고른다'),
        ('2  묶음 · bucket','출처 · 서비스 · 목적지 · 날짜로 나눈다'),
        ('3  계산 · metric','건수 · 고유 값 · 합계 · 평균을 읽는다')],
        '각 수치는 선택한 문서와 묶음의 범위 안에서 해석한다')
    draw('chapter02-observer-flow.png',[
        ('통신 출발지 · data.src_ip','10.20.40.81'),
        ('통신 목적지 · data.dest_ip','53.81.8.74 · data.dest_port = 8888')],
        'agent.name = ips  ·  이 연결을 기록한 관측 출처')
    im=Image.new('RGB',(1500,650),'white');d=ImageDraw.Draw(im)
    f=ImageFont.truetype(str(FONT),48);small=ImageFont.truetype(str(FONT),40)
    for y,title,labels in [(30,'10월 29일 · 전날 표본',['3,711.480초','4,569.310초','2,923.668초']),
                           (330,'10월 30일 · 급증 구간 표본',['32.212초','39.582초','36.993초'])]:
        d.text((45,y),title,font=f,fill='#152a35')
        d.line((70,y+130,1430,y+130),fill='#263a45',width=6)
        for x in (70,520,970,1430):d.rectangle((x-10,y+120,x+10,y+140),fill='#477a80')
        for x,txt in zip((130,580,1030),labels):d.text((x,y+165),txt,font=small,fill='#152a35')
    d.text((45,590),'숫자는 연속 요청 사이의 실제 시각 차이 · 선 길이는 비교용',font=small,fill='#152a35')
    im.save(ROOT/'assets/figures/chapter02-gap-comparison.png')
    shots=ROOT/'assets/screenshots/chapter02'
    Image.open(shots/'index-pattern.png').crop((270,250,825,458)).save(shots/'index-pattern-detail.png')
    Image.open(shots/'terms-console.png').crop((580,445,1148,845)).save(shots/'terms-result-detail.png')
    Image.open(shots/'discover-overview.png').crop((242,410,710,635)).save(shots/'discover-detail.png')
    Image.open(shots/'agent-bars-saved.png').crop((0,145,633,875)).save(shots/'agent-bars-chart.png')
    Image.open(shots/'agent-bars-saved.png').crop((806,325,1143,698)).save(shots/'agent-bars-settings.png')

if __name__=='__main__':build()
