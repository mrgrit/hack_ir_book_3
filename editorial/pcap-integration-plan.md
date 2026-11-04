# PCAP에서 Wazuh 분석까지 연결하는 설계

2026-11-03. 이번 작업에서 공개 악성 PCAP 다운로드·패킷 전송·센서 실행·Wazuh 적재는 하지 않았다. 아래 명령은 공식 문서와 대조한 후속 실습 설계이며 실서버 검증 결과가 아니다.

## 기본 경로와 선택 경로

기본은 **PCAP 파일을 센서가 직접 읽는 오프라인 처리**이다. Suricata는 -r로 캡처를 읽고 EVE JSON을 생성한다. Zeek도 -r로 읽어 conn·dns·http·ssl 등 실제 관측한 프로토콜의 로그를 만든다. 생성된 로그를 Wazuh agent의 localfile로 수집하고, manager의 디코딩·규칙 결과를 확인한다. 모든 네트워크 이벤트가 경보가 되는 것은 아니므로 원문 보관 경로와 경보 경로의 건수를 따로 센다.

패킷을 인터페이스에 실제로 흘리는 실습은 별도의 폐쇄된 분석 VM에서 선택한다. 송신/수신 network namespace와 veth만 연결하고 물리 NIC·VMware Bridged·기본 경로와 연결하지 않는다. 기존 1·2권 kt66 네트워크를 재생 경로로 쓰지 않는다. 목적은 센서의 인터페이스 수신을 확인하는 것이며 공격 대상 서비스를 실행하는 것이 아니다.

| 경로 | 장점 | 확인할 한계 |
|---|---|---|
| Suricata -r | 전송 없이 패킷 시각과 내용을 분석 | 규칙 버전·HOME_NET·체크섬·재조립·손상 패킷 |
| Zeek -r | 연결과 응용 프로토콜 기록을 연계 | 암호화·캡처 누락·비대칭 관측·프로토콜 식별 |
| tcpreplay → 폐쇄 veth → 센서 | 입력 인터페이스·재생 속도에 따른 수집 확인 | 원래 캡처와 재생 수집 시각이 다름, TCP 상대가 응답하는 실세션은 아님 |
| 센서 로그 → Wazuh | 디코더·규칙·수집 지연 확인 | 이벤트 시각과 manager 도착 시각, 경보 미생성 로그의 보관 |

## 후보 자료의 역할

| 자료 | 교재에서의 역할 | 선정 때 확인 |
|---|---|---|
| Malware-Traffic-Analysis.net | 감염 PC와 C2의 사건 중심 조사, 원문으로 돌아가는 문제 | 개별 exercise의 설명·PCAP·정답·배포 조건, 캡처 날짜 |
| Netresec PCAP Files | 다양한 교육 캡처의 출처 색인 | 원 제공자의 데이터 설명·권리·전체/부분 캡처 여부 |
| Contagio | 과거 악성 행위의 참고 자료 | PCAP와 실행 파일을 구분. 이번 실습에는 실행 샘플이 필요 없음 |
| Stratosphere MCFP / IoT-23 | 봇넷·IoT·정상 반례와 라벨 비교 | 라벨의 관측 단위·시나리오·캡처 환경. 네트워크 flow 라벨을 호스트 전체에 확대하지 않기 |
| CAIDA | 큰 규모·DDoS의 빈도·팬아웃·시간 구간 비교 | 데이터별 신청·사용 조건, 익명화·payload 제거. 모든 공격 단계의 원문이 있는 자료로 소개하지 않기 |
| Dynamite Lab | 공개 PCAP 분석 결과와 로컬 결과 비교 후보 | 2026-11-03 웹 조회에서 502 응답. 현재 공개 열람·다운로드·업로드 정책을 확인하기 전 필수 실습에서 제외 |

원본 PCAP를 저장소에 재배포하지 않고 출처 링크·해시·선택 이유·필요 파일 이름을 둔다. 2019 집계 표본은 장기 활동의 근거, PCAP는 짧은 시간의 프로토콜·간격 근거로 사용한다. 서로 다른 조직·시기의 자료를 하나의 실제 사건으로 합치지 않는다.

## 먼저 기록할 항목

dataset-manifest.example.json을 복사하여 자료명·원 URL·제공자 이용 조건·라이선스·SHA-256·파일 크기·패킷 수·첫/마지막 패킷 시각·타임스탬프 정밀도·링크 유형·snaplen·절단 패킷 수를 채운다. capinfos는 Wireshark에 포함된 캡처 통계 도구이다. sha256sum은 파일 바이트의 동일성을 확인한다. 원본과 분석 사본의 해시가 같아야 한다.

실행 위치는 독립 Ubuntu 분석 VM의 ~/book3-pcap이다. 이 VM의 Suricata·Zeek·Wireshark CLI·tcpreplay는 분석자가 준비하며 kt66에 자동 설치돼 있다고 가정하지 않는다. 도구 설치는 선정한 버전과 배포판을 확정한 뒤 별도 준비 절차로 검증한다.

```bash
suricata -V
zeek --version
capinfos input/sample.pcap
sha256sum input/sample.pcap
```

네 명령은 순서대로 Suricata 버전, Zeek 버전, 캡처 메타데이터, 해시를 출력한다. capinfos의 시간 표시는 실행 환경의 시간대 영향을 확인하고 UTC 변환값도 기록한다. 명령을 찾지 못하면 패키지 설치 여부와 실행 경로를 먼저 확인한다.

## 오프라인 로그 생성

사전 확인: input/sample.pcap의 해시, config/suricata.yaml과 rules/book3.rules의 존재·해시를 확인한다. 설정은 별도 사본이며 원본 센서 서비스 파일을 편집하지 않는다. HOME_NET은 캡처에서 관측한 내부망을 기준으로 지정한다. EVE에 alert·flow·dns·http·tls 종류가 필요한지 설정에서 확인한다. HTTP 파일 추출이나 외부 연동은 이 절차에 필요하지 않다.

mkdir은 새 디렉터리를 만든다. 아래 출력 경로가 이미 있으면 다른 실행 이름을 정한다. -p를 사용해 기존 결과에 계속 쓰지 않는다.

```bash
mkdir output
mkdir output/suri-run01
suricata -T -c config/suricata.yaml -S rules/book3.rules
suricata -r input/sample.pcap -c config/suricata.yaml -S rules/book3.rules -l output/suri-run01
```

- -T는 설정·규칙을 시험한다. -c는 설정 파일, -S는 지정한 규칙 파일만 읽는 옵션이다. 설치된 다른 규칙을 더하는 -s와 구분한다.
- -r은 파일 입력이다. -l은 출력 디렉터리이다. 실제 인터페이스에 패킷을 전송하지 않는다.
- eve.json, stats.log, suricata.log에서 종료·처리량·오류를 확인한다. alert 0건은 처리 실패와 같은 뜻이 아니다. 캡처 패킷 수, 디코더 오류·재조립·경보 수를 함께 기록한다.
- -k none은 체크섬 검사를 끈다. 기본 명령에는 넣지 않는다. 송신 측 오프로딩으로 잘못 저장된 체크섬이라는 근거가 있을 때 별도 실행으로 비교하고 사용 사실을 기록한다.

Zeek는 실행 디렉터리에 로그를 만든다. cd는 현재 작업 위치를 바꾸며 ..는 상위 디렉터리이다.

```bash
mkdir output/zeek-run01
cd output/zeek-run01
zeek -r ../../input/sample.pcap LogAscii::use_json=T
cd ../..
```

LogAscii::use_json=T는 로그를 한 행당 JSON 객체로 출력하는 설정이다. conn.log의 uid를 같은 실행의 dns.log·http.log 등에 연결한다. 서로 다른 재실행의 uid가 항상 같다고 가정하지 않는다. -C는 체크섬 검사를 무시하는 선택이며 기본에는 넣지 않는다. 성공 기준은 존재하는 프로토콜 로그의 파싱과 conn uid 연계 확인이다. 캡처에 없는 프로토콜의 로그를 필수 출력으로 요구하지 않는다.

## Wazuh 수집 연결

수집 경로의 가독성과 agent 프로세스의 접근 권한을 먼저 확인한다. 예제 localfile은 전용 분석 agent의 /var/ossec/etc/ossec.conf 안에 추가할 설정 조각이다. 그 파일을 이 조각으로 통째로 덮지 않는다. 설정 사전 사본과 변경 내역을 보존하고 문법 확인 후 해당 agent만 재시작한다. 현재 공동 SIEM에는 적용하지 않는다.

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/book3/suricata/eve.json</location>
</localfile>
```

agent가 감시를 시작한 뒤, 검증한 EVE를 전용 경로에 순서대로 추가하는 절차를 후속 실험에서 확인한다. 기존 파일의 처음부터 읽기 여부·읽기 위치·재시작·회전 동작은 agent 설정과 버전에 따라 검증한다. 무조건 파일 전체가 다시 수집된다고 가정하지 않는다.

manager의 Suricata 규칙은 EVE를 분석한다. Zeek JSON은 JSON 디코딩 가능 여부와 필드별 사용자 규칙을 따로 설계해야 한다. JSON 파싱 성공만으로 네트워크 경보가 자동 완성된다고 설명하지 않는다. 원시 EVE timestamp와 Wazuh 경보 timestamp를 함께 보존한다. 과거 캡처의 날짜를 현재로 덮어쓰는 대신 원래 시각·재생 기준시각·시간 변환을 별도 필드와 manifest에 둔다.

Discover의 관찰은 실제 적용 후 촬영한다. 동일한 실행 ID와 원본 해시로 연결된 원문·decoded data·rule.id를 대조한다. Wazuh archives 수집·색인이 필요한 경우 저장량과 보관 정책을 먼저 정하며 전역 설정을 이번 작업에서 켜지 않는다.

## 선택 실습인 폐쇄망 패킷 재생

ip는 Linux 네트워크 인터페이스와 네임스페이스를 관리하는 도구이다. namespace는 독립된 네트워크 스택이고 veth는 양 끝을 연결하는 가상 인터페이스 쌍이다. sudo는 이 실습에 필요한 관리자 권한을 부여한다. 먼저 ip netns list와 ip link show에서 아래 이름이 사용 중인지 확인한다. 사용 중이면 중단하고 새 실습 이름을 정한다.

```bash
sudo ip netns add b3-tx
sudo ip netns add b3-rx
sudo ip link add b3-tx0 type veth peer name b3-rx0
sudo ip link set b3-tx0 netns b3-tx
sudo ip link set b3-rx0 netns b3-rx
sudo ip netns exec b3-tx ip link set b3-tx0 up
sudo ip netns exec b3-rx ip link set b3-rx0 up
sudo ip netns exec b3-tx ip route show
sudo ip netns exec b3-rx ip route show
```

add는 새 네임스페이스/장치를 만들고, type veth peer name은 짝을 지정한다. set ... netns는 해당 끝을 옮긴다. netns exec는 지정 스택에서 뒤 명령을 실행한다. up은 인터페이스를 올린다. 양쪽에는 IP 주소와 기본 경로를 설정하지 않는다. route 출력이 비어 있고 물리 인터페이스가 보이지 않는지 확인한다. 수신 센서는 전용 설정과 빈 로그 디렉터리로 b3-rx0에서 실행한다.

독립 분석 VM의 첫 터미널에서 다음을 실행한다. 두 link show 결과에는 각 네임스페이스의 lo와 veth 한 끝만 있어야 한다. output은 앞 절에서 만든 디렉터리이다. suri-live01이 이미 있으면 새 이름을 선택한다.

```bash
sudo ip netns exec b3-tx ip link show
sudo ip netns exec b3-rx ip link show
mkdir output/suri-live01
sudo ip netns exec b3-rx suricata -i b3-rx0 -c config/suricata.yaml -S rules/book3.rules -l output/suri-live01
```

Suricata의 -i는 수신 인터페이스를 지정한다. 실행 디렉터리는 ~/book3-pcap이며 네트워크 네임스페이스는 파일 경로를 바꾸지 않는다. 초기화 오류가 없고 센서가 실행 중인 상태에서 다음 재생을 시작한다. 출력은 루트 소유로 생길 수 있으므로 결과를 읽을 권한도 확인한다.

tcpreplay는 캡처에 저장된 패킷을 선택한 인터페이스로 전송한다. 수신 센서 준비를 확인한 뒤 독립 분석 VM의 다른 터미널에서 실행한다.

```bash
sudo ip netns exec b3-tx tcpreplay --intf1=b3-tx0 --multiplier=1 input/sample.pcap
```

--intf1은 첫 송신 인터페이스, --multiplier=1은 기록된 간격의 1배 속도이다. 처음에는 loop·topspeed·pps를 사용하지 않는다. 변환하거나 재생하면 캡처의 사건 시각과 센서 수신 시각이 달라짐을 기록한다. tcpreplay의 패킷 전송은 새로운 서버 TCP 세션·로그인·애플리케이션 실행을 성립시키지 않는다.

완료 후 센서를 Ctrl+C로 정상 종료하고 ip netns pids b3-tx, ip netns pids b3-rx로 프로세스가 남지 않았는지 확인한다. 이번에 만든 두 네임스페이스만 ip netns delete로 제거하고 목록에서 사라졌는지 확인한다. 전용 설정·로그는 해시와 함께 증거로 남긴다. 전용 agent의 수집 설정은 사전 사본과 대조해 추가분만 원상복구한다.

```bash
sudo ip netns pids b3-tx
sudo ip netns pids b3-rx
```

두 출력이 모두 비어 있을 때만 다음 원상복구를 한다. PID가 있으면 해당 실습 프로세스의 터미널로 돌아가 종료 상태를 확인한다.

```bash
sudo ip netns delete b3-tx
sudo ip netns delete b3-rx
ip netns list
```

delete는 지정 네임스페이스를 제거한다. 두 끝을 담은 네임스페이스가 해제되면 해당 veth 쌍도 제거된다. 마지막 목록에서 이번 두 이름이 사라졌는지 확인한다.

## PCAP만으로 만들 수 없는 증거

암호화된 HTTPS에서 복호화 키 없이 URL·본문을 얻었다고 쓰지 않는다. 패킷 재생으로 Windows 프로세스 생성·Linux audit·FIM·서버 로그인 성공 기록이 저절로 생기지 않는다. 그런 자료를 합성해서 덧붙일 때는 ‘합성 호스트 증거’로 따로 표시하고 실제 캡처 증거와 구분한다. 여러 센서가 같은 요청을 기록한 건수와 실제 요청 횟수도 구분한다.

참고자료:

- Malware-Traffic-Analysis exercises: https://www.malware-traffic-analysis.net/training-exercises.html
- Netresec Public PCAP files: https://www.netresec.com/?page=PcapFiles
- Contagio: https://contagiodump.blogspot.com/
- Stratosphere MCFP: https://www.stratosphereips.org/datasets-malware
- Stratosphere IoT-23: https://www.stratosphereips.org/datasets-iot23
- CAIDA catalog: https://catalog.caida.org/search?query=types=dataset%20links=tag:caida%20
- CAIDA DDoS 2007: https://www.caida.org/catalog/datasets/ddos-20070804_dataset/
- Dynamite Lab: https://lab.dynamite.ai/
- Suricata command line: https://docs.suricata.io/en/latest/command-line-options.html
- Zeek quick start: https://docs.zeek.org/en/current/quickstart.html
- Wazuh Suricata integration: https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html
- Tcpreplay timing: https://tcpreplay.appneta.com/reference/man/tcpreplay/
- ip-netns: https://man7.org/linux/man-pages/man8/ip-netns.8.html


## 2026-11-04 12장 후속 검증

12장에서는 MTA 2025-01-22 PCAP를 별도 Ubuntu 폴더에서 파일 분석했다. Suricata 6.0.4·Zeek 8.0.0, Wazuh logtest와 새 전용 인덱스 조회를 검증했다. 패킷 송신·선택 veth 재생·agent 설정 적용은 하지 않았다. 초기 계획의 미실행 표기는 착수 당시 상태이며 상세 결과는 chapter12-review.md에 있다.
