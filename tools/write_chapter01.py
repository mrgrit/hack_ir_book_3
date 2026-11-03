"""Original Korean manuscript and copyable inputs for volume 3 chapter 1."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
pages=[];inputs=[]
def p(t):return {'type':'p','text':t}
def h(t):return {'type':'h','text':t}
def tab(head,rows,widths):return {'type':'table','head':head,'rows':rows,'widths':widths}
def pic(path,caption,width=127):return {'type':'image','path':path,'caption':caption,'width_mm':width}
def code(t):return {'type':'code','text':t}
def cmd(n,text,purpose,syntax,result):
    b={'type':'command','id':f'C03-01-{n:02}','where':'Ubuntu 분석 VM 터미널','text':text,'purpose':purpose,'syntax':syntax,'result':result}
    inputs.append(b);return b
def page(title,*blocks):pages.append({'kind':'content','title':title,'blocks':list(blocks)})
def link(title,url):return {'type':'link','text':title,'url':url}

page('1장 로그 분석용 데이터 준비',
 p('웹 서버가 외부 주소로 반복해서 연결한 기록을 받았다고 하자. 조사자는 연결한 횟수, 활동한 날짜, 간격과 전송량을 비교한다. 요청 한 건을 읽는 것만으로는 몇 주 동안 반복된 통신을 찾기 어렵다.'),
 p('3권에서는 로그를 생성하거나 저장된 패킷에서 관측 로그를 만든 뒤 Wazuh 환경에서 검색하고 집계한다. 집계는 여러 기록을 조건에 따라 묶어 건수·고유 값의 수·전송량 같은 지표를 계산하는 작업이다. 공격 도구를 실제 서비스에 실행하는 대신 기록에 남은 관계를 조사한다.'),
 p('먼저 90일치 학습 데이터를 로컬 파일로 만들고 기간·건수·시간순 정렬·해시를 확인한다. 완료 조건은 검사 결과가 pass이고 생성 조건과 파일의 의미를 설명할 수 있는 상태이다.'),
 pic('assets/illustrations/offline-preparation.png','그림 1-1  오프라인 분석 장비 준비',85),
 p('생성 파일은 이후 집계 실습의 입력이다. 실습용 이벤트에 들어 있는 rule 값과 보안 도구가 실제로 만든 경보를 구분하여 읽는다.'))

page('1.1 조사에 사용할 세 종류의 기록',
 p('purple-agg는 웹·인증·메일·DNS·네트워크 흐름 등의 기록을 만드는 학습용 Python 프로그램이다. 생성기는 시나리오의 행위와 운영 배경을 함께 만든다. 파일에 로그인 성공이 적혀 있어도 실제 서버에 로그인한 결과를 뜻하지 않는다.'),
 pic('assets/figures/evidence-paths.png','그림 1-2  학습 데이터와 관측 로그의 생성 경로'),
 p('원문 로그를 Wazuh manager에 보내면 디코더가 필드를 추출하고 규칙이 경보 조건을 평가한다. PCAP는 저장된 패킷 파일이다. PCAP를 Suricata나 Zeek 같은 네트워크 분석 도구로 읽으면 패킷에서 관측한 통신 기록을 얻는다.'),
 p('직접 만든 이벤트로는 검색·집계의 판단을 연습한다. 디코더와 규칙의 동작은 원문을 실제로 처리한 결과로 확인한다.'))

page('1.2 사건 시각과 수집 시각',
 p('기록의 timestamp를 읽기 전에 어느 시각을 나타내는지 확인한다. 사용자 동작이 발생한 때, 센서가 관측한 때, 수집 서버에 도착한 때는 서로 다를 수 있다.'),
 pic('assets/figures/three-times.png','그림 1-3  사건과 관측 및 수집의 시각',114),
 p('생성 파일의 timestamp는 시나리오에 지정한 사건 시각이다. 프로그램을 오늘 실행해도 과거 90일의 기록을 만들 수 있다. 오늘 생성했다는 이유로 검색 기간을 오늘로 지정하면 학습 데이터가 보이지 않을 수 있다.'),
 p('원래 한 시간 간격이던 기록을 한 번에 수집하면 도착 간격은 매우 짧아진다. 이벤트 시각을 사용하는 집계와 manager의 수신 과정에 영향을 받는 상관 규칙을 같은 시간 기준으로 판단하지 않는다.'))

page('1.3 실행 위치와 준비 상태',
 p('파일 생성에는 Ubuntu 22.04 분석 VM의 터미널을 사용한다. 기존 kt66 VM을 사용할 수 있지만 생성 과정에는 Wazuh 접속이 필요하지 않다. 공격자 VM과 attacker 컨테이너도 필요하지 않다. 이후 대시보드는 Windows 브라우저에서 kt66 주소로 접속한다.'),
 p('Python 3는 생성 프로그램을 실행한다. Git은 저장소를 내려받고 사용할 코드 버전을 확인한다. 두 도구는 다음 명령으로 준비 상태를 먼저 확인한다.'),
 cmd(1,'python3 --version','Python 3 실행 가능 여부를 확인한다.','--version은 버전만 출력한다. 파일이나 서버 설정을 바꾸지 않는다.','Python 3.x가 출력된다. command not found이면 분석 VM의 Python 설치 상태와 실행 경로를 확인한다.'),
 cmd(2,'git --version','Git 실행 가능 여부를 확인한다.','git은 버전 관리 도구이다. --version은 설치된 Git의 버전을 출력한다.','git version 뒤에 버전이 나온다. 명령을 찾지 못하면 Git을 준비한 뒤 계속한다.'),
 p('3권의 준비 도구는 Python 표준 라이브러리만 사용한다. 저자용 DOCX 조판 도구와 실제 XLSX 통계 추출 도구의 추가 패키지는 이 실습에 필요하지 않다.'))

page('1.4 교재 파일 내려받기',
 p('홈 디렉터리 아래에 교재 저장소와 강의 코드 사본을 각각 둔다. 홈 디렉터리는 로그인한 사용자의 작업 공간이며 셸의 물결표(~)로 나타낸다. 기존 폴더가 있으면 그 내용을 먼저 확인하고 새 clone으로 덮어쓰지 않는다.'),
 cmd(3,'ls -ld ~/hack_ir_book_3','교재 작업 폴더가 이미 있는지 확인한다.','ls는 파일 정보를 보여 준다. -l은 자세히, -d는 폴더 내부 대신 폴더 자체를 표시한다.','기존 폴더가 있으면 내용을 확인해 사용한다. 처음 작업할 때 No such file or directory는 아직 없다는 뜻이다.'),
 cmd(4,'git clone \\\n  https://github.com/mrgrit/hack_ir_book_3.git \\\n  ~/hack_ir_book_3','교재의 프로그램과 복사용 예제를 내려받는다.','clone 다음에는 원격 주소와 새 폴더 경로를 쓴다. 줄 끝의 역슬래시(\\)는 다음 줄까지 한 명령으로 이어 준다. 역슬래시 뒤에는 공백을 넣지 않는다.','작업이 완료되면 ~/hack_ir_book_3에 tools와 examples가 있다. 인증·접속 오류이면 계정 접근 권한과 네트워크를 확인한다.'),
 cmd(5,'cd ~/hack_ir_book_3','이후 명령의 기준 위치를 교재 저장소로 바꾼다.','cd는 현재 디렉터리를 바꾼다. 이후의 tools/...와 build/...는 이 디렉터리 아래 경로이다.','오류 없이 프롬프트가 돌아오면 다음 명령으로 현재 위치를 확인한다.'),
 cmd(6,'pwd','현재 작업 위치를 확인한다.','pwd는 현재 디렉터리의 전체 경로를 출력한다.','경로 끝이 /hack_ir_book_3이어야 한다. 다르면 C03-01-05부터 다시 확인한다.'))

page('1.5 생성기 원본 버전 고정',
 p('강의 저장소의 purple-agg 디렉터리에는 공통 엔진과 13개 라운드가 있다. 교재 준비 도구는 이 코드를 읽어 파일을 만들며 강의 코드를 수정하지 않는다. 먼저 ~/hack_ir_with_wazuh_source가 기존 작업 폴더인지 확인한다.'),
 cmd(7,'ls -ld ~/hack_ir_with_wazuh_source','원본 코드 사본의 대상 폴더를 확인한다.','-ld는 폴더 자체를 자세히 표시한다.','폴더가 없을 때 다음 clone을 실행한다. 기존 폴더가 있으면 작업 내용과 Git 상태를 먼저 확인한다.'),
 cmd(8,'git clone \\\n  https://github.com/mrgrit/hack_ir_with_wazuh.git \\\n  ~/hack_ir_with_wazuh_source','강의 코드를 별도 사본으로 내려받는다.','마지막 경로가 저장 위치이다. 교재 저장소와 다른 폴더를 지정한다.','복제가 완료되면 purple-agg 디렉터리가 있다.'),
 cmd(9,'git -C ~/hack_ir_with_wazuh_source \\\n  checkout --detach \\\n  d6a2397fc31517147ddd09f58e0d153bc8cf0588','교재에서 사용할 생성기 버전을 선택한다.','-C는 지정한 폴더에서 Git을 실행한다. checkout --detach는 브랜치의 최신 상태 대신 지정 커밋을 읽는 상태로 전환한다. 새 사본에서 실행한다.','HEAD가 지정 커밋으로 이동한다. 로컬 변경을 덮을 수 있다는 메시지가 나오면 중단하고 변경 파일부터 확인한다.'))

page('1.6 생성 조건 결정',
 cmd(10,'git -C ~/hack_ir_with_wazuh_source rev-parse HEAD','선택한 코드 버전을 확인한다.','rev-parse HEAD는 현재 커밋의 전체 식별자를 출력한다.','d6a2397fc31517147ddd09f58e0d153bc8cf0588과 일치해야 한다.'),
 p('난수로 만든 데이터도 같은 조건을 고정하면 다시 만들 수 있다. seed는 난수의 시작 상태를 정하는 값이다. R01은 seed 101을 사용한다. 코드 버전·기준일·기간·규모 배율·프로파일도 함께 고정한다.'),
 tab(['조건','이 실습의 값과 의미'],[
 ['라운드','R01. 운영 배경과 서버발 반복 통신을 함께 만든다.'],
 ['기준일','2026-11-01 00:00:00 +09:00. 이 시각은 데이터 구간에 포함하지 않는다.'],
 ['기간','90일. 2026-08-03 00:00:00부터 기준일 직전까지이다.'],
 ['규모 배율','0.005. 처음에는 작은 외부 방문자 풀로 생성한다.'],
 ['실행 이름','pilot01. 이후 전용 인덱스 이름에도 사용한다.']],[28,99]),
 p('규모 배율은 모든 이벤트를 같은 비율로 줄이는 값이 아니다. 시나리오와 일부 운영 이벤트는 그대로 남는다. 따라서 작은 파일의 시나리오 비율을 실제 환경의 공격 비율로 해석하지 않는다.'))

page('1.7 로컬 학습 파일 생성',
 p('prepare_round.py는 원본 생성기를 읽어 이벤트를 만들고 전체를 시간순으로 정렬하는 교재용 도구이다. bulk 파일은 한 번에 여러 문서를 저장하도록 구성한 입력 형식이다. 이 도구는 파일만 만들며 Wazuh에 요청을 보내지 않는다.'),
 cmd(11,'ls -ld build/r01-pilot01','출력 폴더가 이미 있는지 확인한다.','build는 생성 결과를 두는 폴더이고 r01-pilot01은 이번 실행의 결과 폴더이다.','처음에는 폴더가 없어야 한다. 기존 결과가 있으면 아래 명령의 실행 이름과 출력 폴더를 새 이름으로 바꾼다.'),
 cmd(12,'python3 tools/prepare_round.py \\\n  --source ~/hack_ir_with_wazuh_source/purple-agg \\\n  --round r01 --anchor 2026-11-01 \\\n  --days 90 --scale 0.005 \\\n  --run-id pilot01 --out build/r01-pilot01','R01의 90일 학습 파일을 생성한다.','--source는 원본 폴더, --round는 라운드, --anchor는 끝 기준일, --days는 기간, --scale은 규모 배율이다. --run-id는 실행 이름, --out은 새 결과 폴더이다.','완료 출력의 total과 counts를 기록한다. 이 조건의 R01은 총 85,306건, background 83,044건, scenario 2,262건이다.'),
 p('실행 이름은 소문자·숫자·하이픈으로 정한다. 생성 도중 중단되면 같은 출력 폴더가 완성됐는지 확인한 뒤 재시도한다. 이미 완성된 폴더가 있으면 도구가 덮어쓰기를 거부한다.'))

page('1.8 생성 파일 검사',
 tab(['파일','읽는 목적'],[
 ['events.bulk.ndjson','적재 동작 한 행과 이벤트 한 행이 번갈아 들어 있다.'],
 ['truth.jsonl','같은 이벤트 ID로 연결되는 시나리오·배경 구분이다.'],
 ['manifest.json','생성 조건, 건수, 시간 범위, 파일 해시를 기록한다.'],
 ['template.json','이 실행의 전용 인덱스에 사용할 필드 형식이다. 아직 서버에 적용한 상태가 아니다.']],[49,78]),
 p('JSON은 이름과 값으로 데이터를 표현하는 형식이다. NDJSON과 JSONL은 JSON 객체를 한 행씩 저장한다. 해시는 파일 바이트를 계산한 식별값이다. 내용이 바뀌면 같은 해시로 확인되지 않는다.'),
 cmd(13,'python3 tools/check_dataset.py build/r01-pilot01','생성 파일의 손상과 시간·건수 불일치를 검사한다.','check_dataset.py 다음에는 검사할 결과 폴더를 지정한다. 해시, 이벤트 ID와 정답 연결, 기간 및 전체 순서를 검사한다.','status가 pass이고 events가 85306이다. chronological과 hashes_verified가 true인지 확인한다.'),
 code('"status": "pass"\n"events": 85306\n"chronological": true\n"hashes_verified": true'),
 p('검사 통과는 파일의 일관성이 맞다는 뜻이다. Wazuh 규칙이 이 기록을 탐지했다는 뜻은 아니다.'))

page('1.9 이벤트 한 건 읽기',
 p('inspect_events.py는 bulk 파일에서 이벤트를 골라 터미널에 출력한다. bulk의 저장 동작을 서버로 보내지는 않는다. 먼저 웹 접근 기록 한 건을 확인한다.'),
 cmd(14,'python3 tools/inspect_events.py \\\n  build/r01-pilot01 \\\n  --decoder web-accesslog --limit 1','웹 접근 이벤트의 원문과 필드를 확인한다.','--decoder는 decoder.name의 정확한 값을 지정한다. --limit 1은 한 건만 출력한다.','event 안의 timestamp, agent, decoder, data, full_log와 book3를 읽는다. 일치하는 이벤트가 없으면 decoder 이름과 결과 폴더를 확인한다.'),
 tab(['필드','첫 이벤트의 값과 역할'],[
 ['timestamp','2026-08-03T00:00:21.234+0900. 합성 사건 시각이다.'],
 ['agent.name','juiceshop. 학습 시나리오에서 기록을 남긴 호스트 역할이다.'],
 ['decoder.name','web-accesslog. 원본 생성기가 붙인 해석 형식이다.'],
 ['location','/var/log/apache2/juiceshop_access.log. 시나리오의 로그 위치이다.'],
 ['book3.synthetic','true. 합성 학습 데이터라는 표시이다.']],[44,83]),
 p('이 파일의 agent와 decoder 값은 실제 에이전트의 접속 확인이나 manager의 디코딩 시험 결과가 아니다. 현재 가동 중인 호스트 상태는 별도로 확인한다.'))

page('1.10 원문과 추출 필드 대조',
 p('첫 웹 이벤트의 full_log에는 아래와 같은 정보가 들어 있다. 주소는 생성기가 만든 학습 값이다. 실제 위협 주소 목록으로 사용하지 않는다.'),
 code('138.177.71.203 - -\n[03/Aug/2026:00:00:21 +0900]\n"GET / HTTP/1.1" 200 10660\n"-" "Pingdom.com_bot_version_1.4_..."'),
 p('실제 full_log는 한 문자열이며 위 값은 구조를 읽기 위한 발췌이다. 전체 User-Agent와 원문은 C03-01-14의 출력에서 확인한다.'),
 tab(['원문의 위치','연결되는 필드와 해석'],[
 ['첫 주소','data.srcip. 요청 출발지이다. agent.ip는 기록을 남긴 호스트의 주소이므로 역할이 다르다.'],
 ['대괄호 안 날짜','요청 시각과 +0900 시간대이다. 원문에는 초까지만 있고 timestamp에는 합성 밀리초가 추가돼 있다.'],
 ['GET / HTTP/1.1','data.protocol은 GET, data.url은 /이다. HTTP/1.1은 HTTP 버전이다.'],
 ['200 10660','data.id는 HTTP 상태 200, data.bytes는 응답 바이트 수이다. rule.id와 data.id는 다른 값이다.']],[37,90]),
 p('duration_ms와 GeoLocation은 이 full_log에서 그대로 추출한 값이 아니다. 생성기가 별도로 부여한 처리 시간과 지리 정보이다. User-Agent도 요청자가 바꿀 수 있으므로 문자열 하나로 정상 모니터임을 확정하지 않는다.'))

page('1.11 횟수와 시간 간격의 의미',
 p('집계 표본을 생성기의 근거로 사용할 때는 무엇을 센 표인지 먼저 확인한다. 하루 동안의 요청 수, 여러 달 동안 활동한 날짜 수, 집계된 행 수는 서로 다른 수량이다. 같은 출발지가 여러 날짜의 누적 표에 나타날 때 행을 모두 더하면 중복될 수 있다.'),
 p('제공된 실제 표본의 세 날짜에서 활동 일수로 나눈 출발지 비율은 다음과 같다. 활동 1일은 요청 1회와 같은 뜻이 아니다.'),
 tab(['표본','1일 활동','2~14일','15일 이상'],[
 ['5월 26일','64.99%','23.99%','11.02%'],
 ['5월 27일','37.60%','38.66%','23.74%'],
 ['5월 30일','28.94%','48.64%','22.42%']],[34,31,31,31]),
 p('비율이 다른 이유는 관측 대상과 기간, 수집 범위에도 있을 수 있다. 이 표를 인터넷 전체의 공격자 비율로 일반화하지 않는다. 보안 장비가 관측한 집계의 특성과 애플리케이션 전체 이용자의 특성도 구분한다.'),
 p('분 단위 집계 간격을 초 단위 요청 간격으로 사용하면 빈도가 달라진다. 평균과 표준편차만으로 요청의 원래 순서를 복원할 수도 없다. 정의와 단위가 확인된 장기 활동 통계는 재방문 모델에, 원시 기록의 간격은 세션 모델에 연결한다.'),
 p('생성 데이터의 현실성은 숫자를 무작위로 바꾸는 것만으로 높아지지 않는다. 실패 후 재시도, 성공 뒤의 후속 행동, 작업 중단과 정상 점검 같은 조건을 함께 확인해야 한다.'))

page('1.12 분석에 넘기기 전 확인',
 pic('assets/figures/preparation-flow.png','그림 1-4  생성 파일의 준비와 인계',102),
 p('manifest의 scenario는 원본 생성기의 시나리오 함수에서 나온 기록이라는 뜻이다. R15에는 승인된 스캔과 정상 백업도 이 경로에 포함된다. background에도 인터넷 스캔과 인증 실패가 섞인다. 두 값을 악성·정상의 정답으로 치환하지 않는다.'),
 p('분석자는 이벤트 파일을 먼저 읽고 자신의 근거를 기록한다. 정답 파일은 이후 결과를 대조할 때 사용한다. 시간 범위와 파일 해시가 다른 결과를 비교하기 전에 생성 조건부터 맞춘다.'))

page('1.13 Wazuh 분석에 필요한 인계 정보',
 p('Wazuh indexer는 검색할 문서를 저장하고 대시보드는 그 문서를 조회한다. index는 문서가 저장된 논리적 단위이다. 이 실습의 예정 이름은 book3-r01-pilot01이다. 로컬 파일을 생성한 것만으로 서버에 이 index가 생기지는 않는다.'),
 tab(['인계 항목','확인할 내용'],[
 ['데이터 이름','book3-r01-pilot01과 manifest의 index 값'],
 ['기간','2026-08-03 00:00:00 이상, 2026-11-01 00:00:00 미만, +09:00'],
 ['건수','85,306개 이벤트. bulk 파일의 줄 수와 구분한다.'],
 ['출처','생성기 커밋, R01, seed 101, 90일, scale 0.005'],
 ['필드 형식','template.json의 timestamp는 date, 집계 대상 문자열은 keyword'],
 ['검증 기록','check_dataset의 pass와 manifest의 파일별 SHA-256']],[31,96]),
 p('bulk 파일의 create는 같은 ID의 문서가 있으면 덮어쓰지 않고 충돌을 알리는 저장 동작이다. 이후 적재 단계에서 응답 전체와 항목별 오류를 확인해야 한다. 기존 데이터가 있는 공용 index를 지우고 다시 만드는 방식은 다른 실습 결과에 영향을 준다.'),
 p('공동 실습 환경에서 index의 식별자나 문서 수가 예기치 않게 바뀌면 다른 작업의 완료를 기다린다. 인계한 파일을 보존하고 작업 시간대와 전용 index를 정한 다음 집계 실습을 진행한다.'))

page('1.14 실패 확인과 원상복구',
 tab(['관찰한 결과','확인 순서'],[
 ['파일을 찾지 못함','pwd로 교재 경로를 확인한다. 이어 tools 파일과 --source 경로를 확인한다.'],
 ['원본 버전 오류','rev-parse HEAD를 지정 커밋과 비교한다. 원본의 변경 파일도 확인한다.'],
 ['출력 폴더 존재','기존 manifest를 보존하고 실행 이름과 --out을 새 이름으로 지정한다.'],
 ['Hash mismatch','원본을 보존하고 수정·복사 과정을 확인한다. 새 폴더에서 같은 조건으로 재생성한다.'],
 ['건수 불일치','코드·anchor·days·scale·profile을 비교해 서로 다른 실행 결과인지 확인한다.']],[37,90]),
 p('생성 도중 멈추려면 터미널에서 Ctrl+C를 누른다. 완료 결과 폴더와 manifest가 있는지 확인한다. 임시 파일이나 불완전한 폴더를 완료 데이터로 인계하지 않는다. 새 실행 이름으로 재생성한 뒤 검사를 통과한 결과를 선택한다.'),
 p('원상복구할 서버 설정은 없다. 이번 절차가 만든 것은 로컬 결과 파일이다. 완료 결과를 보존용 폴더로 옮길 때는 아래 명령으로 대상부터 확인한다.'),
 cmd(15,'ls -ld build/r01-pilot01','옮길 결과 폴더를 확인한다.','-ld는 지정한 폴더 하나의 정보를 보여 준다.','이번에 만든 결과 경로인지 확인한다. 다른 폴더이면 이동하지 않는다.'))

page('1.15 결과 보존과 완료 판정',
 p('mv는 파일이나 폴더의 위치·이름을 바꾸는 도구이다. 아래 예는 결과 폴더를 보존 이름으로 바꾼다. 새 이름이 이미 있으면 다른 이름을 정한다.'),
 cmd(16,'ls -ld build/r01-pilot01-reviewed','이동할 새 이름의 존재 여부를 확인한다.','대상 폴더가 이미 있는지 표시한다.','No such file or directory이면 새 이름이다. 이미 있다면 아래 명령을 실행하지 않고 다른 이름을 정한다.'),
 cmd(17,'mv -i build/r01-pilot01 \\\n  build/r01-pilot01-reviewed','검사를 마친 결과를 보존 이름으로 옮긴다.','첫 경로가 원본, 둘째 경로가 새 이름이다. -i는 덮어쓰기가 발생할 때 확인을 요구한다. 앞의 대상 확인을 마친 뒤 실행한다.','다음 검사에서 이동한 폴더의 파일 해시가 유지돼야 한다.'),
 cmd(18,'python3 tools/check_dataset.py \\\n  build/r01-pilot01-reviewed','이동 후 데이터가 그대로인지 확인한다.','검사 도구에 새 폴더 경로를 전달한다.','다시 pass가 나오면 보존이 완료된다. 파일 안의 실행 이름과 index 이름은 pilot01로 유지된다.'),
 p('완료 기록에는 총 건수, 시작과 종료 시각, 코드 버전, 검사 결과를 남긴다. 다음 집계 실습에서는 원문 한 건과 집계 결과를 오가며 반복 통신의 후보를 찾는다.'))

page('참고자료',
 link('3권 교재 저장소','https://github.com/mrgrit/hack_ir_book_3'),
 link('purple agg 원본 코드','https://github.com/mrgrit/hack_ir_with_wazuh/tree/d6a2397fc31517147ddd09f58e0d153bc8cf0588/purple-agg'),
 link('집계 기초와 침해분석대응 강의자료','https://drive.google.com/drive/folders/1opod1aNlgA9LW248K-U99VFK9QKBLiH6'),
 link('실제 로그 집계 표본','https://drive.google.com/drive/folders/1fJNfD402l9IRECphaDYX-Y6ca5VH7no0'))

page('참고자료 계속',
 link('OpenSearch Bulk API','https://docs.opensearch.org/latest/api-reference/document-apis/bulk/'),
 link('Wazuh 네트워크 IDS 연계','https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html'),
 link('Suricata 명령행 옵션','https://docs.suricata.io/en/latest/command-line-options.html'),
 link('Zeek 시작 안내','https://docs.zeek.org/en/current/quickstart.html'))

for pg in pages[4:16]:pg['break']=False
data={'title':'1장 로그 분석용 데이터 준비','series':'해킹·침해대응 실무 with Wazuh 3권','comments':'2026-11-03 착수 초안. 오프라인 파일 생성 검증 범위는 editorial 기록 참조.','pages':pages}
(ROOT/'manuscript').mkdir(exist_ok=True)
(ROOT/'manuscript/volume03-chapter01.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=ROOT/'examples/chapter01';out.mkdir(parents=True,exist_ok=True)
for b in inputs:
    text=f"# {b['id']} | {b['where']}\n# {b['purpose']}\n{b['text']}\n"
    (out/(b['id']+'.sh')).write_text(text,encoding='utf-8')
(out/'input-index.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(pages)} planned pages; {len(inputs)} commands')
