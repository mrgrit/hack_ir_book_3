# 해킹·침해대응 실무 with Wazuh — 3권

가제: **로그 생성과 집계 기반 침해분석**. 2026-11-04 기준 **1~13장과 부록 A·B의 초안을 완성했다.** 장별 DOCX 15개, 지면 합계 431쪽이다.

실제 시스템을 공격하지 않고 `purple-agg`가 생성한 학습 데이터와 공개 PCAP에서 센서가 얻는 로그로 조사한다. 생성 이벤트의 `rule` 필드와 Wazuh manager가 실제로 만든 경보를 구분한다.

## 이번 산출물

- [1장 DOCX](manuscript/volume03-chapter01.docx): 로그 분석용 데이터 준비, B5 22쪽. 명령 18개, 도식 3개, 삽화 2개.
- [2장 DOCX](manuscript/volume03-chapter02.docx): 집계 기준과 정상 분포, B5 49쪽. 전용 인덱스 적재, Terms·고유 수·합계·평균·시간 버킷, 반복 연결 후보 조사, 결과 보존과 원상복구를 다룬다. 실제 Wazuh 화면 5개, 도식 3개, 삽화 1개와 [복사용 쿼리 14개](examples/chapter02)를 제공한다.
- [3장 DOCX](manuscript/volume03-chapter03.docx): 정찰과 분산 탐색, B5 25쪽. R02 84,392건에서 출발지·경로·포트·활동 날짜를 비교한다. 실제 조회 9개와 [복사용 예제](examples/chapter03), 조사표를 제공한다.
- [4장 DOCX](manuscript/volume03-chapter04.docx): 웹 침투와 지속성, B5 30쪽. R03 응답 변화와 R04 파일·프로세스·계정·예약 실행을 독립 사례로 조사한다. 실제 조회 12개, [복사용 예제](examples/chapter04)와 생성 시간 간격의 불일치 해석을 제공한다.
- [5장 DOCX](manuscript/volume03-chapter05.docx): 권한 상승과 기록 공백, B5 24쪽. R05 100,739건에서 sudo·감사 기록·빈 시간 버킷·FIM 변경을 비교한다. 실제 조회 8개와 [복사용 예제](examples/chapter05), 수집 복구 판단·조사표를 제공한다.
- [6장 DOCX](manuscript/volume03-chapter06.docx): 자격증명 공격과 피싱, B5 25쪽. R06 86,174건에서 계정 중심 분산 실패·성공·메일 전달·후속 요청을 연결한다. 실제 조회 9개와 [복사용 예제](examples/chapter06), 배경 축소에 따른 분포 변화와 세션 증거의 한계를 다룬다.
- [7장 DOCX](manuscript/volume03-chapter07.docx): 내부 이동, B5 27쪽. R07 82,010건에서 SSH 접속 대상·Windows 로그온·프로세스·계정 변경을 실제 조회 9개와 연결한다. [복사용 예제](examples/chapter07)와 증거 연결의 한계를 제공한다.
- [8장 DOCX](manuscript/volume03-chapter08.docx): 외부 통신과 유출, B5 24쪽. R08 85,945건에서 반복 간격·DNS 이름·방향별 바이트를 실제 조회 8개와 연결한다. [복사용 예제](examples/chapter08)와 로컬 간격 계산 도구를 제공한다.
- [9장 DOCX](manuscript/volume03-chapter09.docx): 장기 사건 재구성, B5 34쪽. R09 101,293건에서 웹·권한·내부 이동·외부 전송·삭제를 실제 조회 10개로 연결한다. [복사용 예제와 시간표](examples/chapter09)를 제공한다.
- [10장 DOCX](manuscript/volume03-chapter10.docx): 대량 파일 변경과 서비스 장애, B5 26쪽. R10 85,969건을 실제 조회 9개로 조사하고 파일 수·장애 관측 공백·응답 크기·GPU 연결의 해석을 다룬다. [복사용 예제](examples/chapter10)를 제공한다.
- [11장 DOCX](manuscript/volume03-chapter11.docx): AI 서비스의 입력과 후속 동작, B5 35쪽. R12 83,101건·R13 101,582건을 실제 조회 13개로 조사하고 입력 표지·도구 권한·내부 요청·고속 웹 요청·서버 인증과 전송을 연결한다. [복사용 예제](examples/chapter11)를 제공한다.
- [12장 DOCX](manuscript/volume03-chapter12.docx): PCAP에서 관측 로그 만들기, B5 36쪽. 공개 캡처 39,427패킷을 Suricata·Zeek로 파일 분석하고 3,746개 관측 문서를 실제 조회 6개로 조사한다. Wazuh logtest와 센서 재조립 설정 비교, [복사용 예제](examples/chapter12), 선택 폐쇄망 재생 절차를 제공한다.
- [13장 DOCX](manuscript/volume03-chapter13.docx): 종합 조사와 대응 판단, B5 34쪽. R15 105,293건을 조회 10개로 조사하고 PC·AI 활동, 승인된 점검·백업을 분리한다. [복사용 예제와 사건표·시간표·모의 대응 계획](examples/chapter13)을 제공한다.
- [부록 A DOCX](manuscript/volume03-appendixA.docx): 필드·명령·조회 색인, B5 19쪽. [조회 117개·본문 명령 83개의 색인](examples/appendixA), 자료형 확인과 오류 확인표를 제공한다.
- [부록 B DOCX](manuscript/volume03-appendixB.docx): 생성 조건과 재현 기록, B5 21쪽. R15 동일 조건 재생성, 실제 표본의 시간·횟수·빈도 해석, PCAP 센서 설정 비교와 [실행 목록·분포 평가·출처·인계 양식](examples/appendixB)을 제공한다.
- [전체 목차와 강의 대응표](editorial/volume03-outline.md): 13장 및 부록의 학습 목표·실습·완료 조건.
- [집필 계획](editorial/authoring-plan.md): 집필 순서와 공동 SIEM 사용 원칙.
- [생성기 현실성 점검](editorial/generator-realism-review.md): 실제 집계 표본 3개와 코드·오프라인 실행의 대조.
- [PCAP 연계 설계](editorial/pcap-integration-plan.md): Suricata·Zeek 파일 분석을 기본으로, 폐쇄 veth 재생을 선택으로 구성.
- [검증 기록](editorial/verification.md): 실행한 검사와 아직 실행하지 않은 범위.

사용자 요청에 따라 **3장부터 13장, 부록 A·B까지 순차 집필·검수했다.** 각 장의 업로드를 마친 뒤 다음 장을 진행했다. [진행 기록](editorial/sequential-authoring.md)과 [최종 파일 대조 기록](editorial/volume03-delivery-verification.json)을 제공한다. 현재 산출물은 교정용 초안이며 합본·PDF 배포 없이 별도 DOCX를 유지한다. REV01과 1·2권 원고는 보존한다.

## 로컬 준비 도구

독자용 명령은 각 장과 [1장 예제](examples/chapter01), [2장 예제](examples/chapter02)에 있다. 다음 명령은 도구를 빠르게 확인할 저자용 예이다. Python 3와 Git이 필요하며 생성·검사·적재 도구에는 Python 표준 라이브러리만 사용한다.

먼저 강의 코드를 **별도 사본**으로 준비하고 다음 커밋을 선택한다. 기존 작업 폴더를 덮어쓰지 않는다.

```bash
git clone https://github.com/mrgrit/hack_ir_with_wazuh.git ../hack_ir_with_wazuh_source
git -C ../hack_ir_with_wazuh_source checkout --detach d6a2397fc31517147ddd09f58e0d153bc8cf0588
python3 tools/prepare_round.py --source ../hack_ir_with_wazuh_source/purple-agg --round r01 --anchor 2026-11-01 --days 90 --scale 0.005 --run-id pilot01 --out build/r01-pilot01
python3 tools/check_dataset.py build/r01-pilot01
```

출력 폴더가 있으면 새 실행 이름과 경로를 선택한다. `prepare_round.py`는 서버 접속 없이 전체 시간순으로 정렬한 bulk 파일, 별도 시나리오 출처 파일, 전용 템플릿 사본, 생성 조건·해시 manifest를 만든다. R01의 위 조건은 85,306건이다. `scenario`와 `background`는 악성/정상 라벨이 아니다. 템플릿과 bulk 파일을 만든 것만으로 Wazuh에 적용되지는 않는다.

실제 집계 표본의 시간 단위는 미확정이다. 이번 도구는 원본 시간 모델을 유지하며 **실측 분포 보정을 완료한 생성기라고 주장하지 않는다**. 발견 사항과 후속 수용 기준은 현실성 점검 문서에 있다.

## 공동 SIEM

1장은 오프라인 파일 준비를 다룬다. 2~13장은 기존 kt66 환경의 전용 인덱스에서 실제 조회와 Wazuh UI를 확인했다. 13개 합성 라운드 1,188,021건과 PCAP 관측 문서 3,746건을 서로 다른 자료로 관리한다. 장별 적재 전에 기존 인덱스의 안정 상태를 확인했으며 기존 자료의 소멸·재생성·건수 감소는 없었다. 기존 규칙·공용 템플릿·서비스를 변경하거나 실제 공격·네트워크 패킷 재생을 수행하지 않았다. 12장의 센서 분석은 별도 컨테이너의 파일 입력으로 검증했다. 상세 범위는 장별 검토 기록과 [검증 기록](editorial/verification.md)에 있다.

원본 `gen`은 같은 라운드 인덱스를 삭제 후 재생성하므로 공동 환경에서 바로 실행하지 않는다. 교재의 `load_dataset.py`는 파일 검사를 마친 뒤 새 전용 인덱스만 만들며, 이미 존재하는 인덱스에서는 중단한다. 로그 소멸이나 UUID·건수의 예상 밖 변동이 있으면 다른 작업이 끝날 때까지 기다린다.

## 재현과 자료

[저자용 재현 절차](editorial/reproduction.md)와 [자료 목록](editorial/source-register.md)을 참조한다. 실자료 원본·개별 식별자·PCAP·대용량 생성물·검수용 PDF는 이 저장소에 배포하지 않는다. 표본 통계와 출처·해시를 제공한다.

- 강의 코드: https://github.com/mrgrit/hack_ir_with_wazuh/tree/d6a2397fc31517147ddd09f58e0d153bc8cf0588/purple-agg
- 강의자료: https://drive.google.com/drive/folders/1opod1aNlgA9LW248K-U99VFK9QKBLiH6
- 실제 집계 표본: https://drive.google.com/drive/folders/1fJNfD402l9IRECphaDYX-Y6ca5VH7no0
