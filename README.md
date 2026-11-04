# 해킹·침해대응 실무 with Wazuh — 3권

가제: **로그 생성과 집계 기반 침해분석**. 2026-11-04 기준 1~4장 초안이다.

실제 시스템을 공격하지 않고 `purple-agg`가 생성한 학습 데이터와 공개 PCAP에서 센서가 얻는 로그로 조사한다. 생성 이벤트의 `rule` 필드와 Wazuh manager가 실제로 만든 경보를 구분한다.

## 이번 산출물

- [1장 DOCX](manuscript/volume03-chapter01.docx): 로그 분석용 데이터 준비, B5 22쪽. 명령 18개, 도식 3개, 삽화 2개.
- [2장 DOCX](manuscript/volume03-chapter02.docx): 집계 기준과 정상 분포, B5 49쪽. 전용 인덱스 적재, Terms·고유 수·합계·평균·시간 버킷, 반복 연결 후보 조사, 결과 보존과 원상복구를 다룬다. 실제 Wazuh 화면 5개, 도식 3개, 삽화 1개와 [복사용 쿼리 14개](examples/chapter02)를 제공한다.
- [3장 DOCX](manuscript/volume03-chapter03.docx): 정찰과 분산 탐색, B5 25쪽. R02 84,392건에서 출발지·경로·포트·활동 날짜를 비교한다. 실제 조회 9개와 [복사용 예제](examples/chapter03), 조사표를 제공한다.
- [4장 DOCX](manuscript/volume03-chapter04.docx): 웹 침투와 지속성, B5 30쪽. R03 응답 변화와 R04 파일·프로세스·계정·예약 실행을 독립 사례로 조사한다. 실제 조회 12개, [복사용 예제](examples/chapter04)와 생성 시간 간격의 불일치 해석을 제공한다.
- [전체 목차와 강의 대응표](editorial/volume03-outline.md): 13장 및 부록의 학습 목표·실습·완료 조건.
- [집필 계획](editorial/authoring-plan.md): 집필 순서와 공동 SIEM 사용 원칙.
- [생성기 현실성 점검](editorial/generator-realism-review.md): 실제 집계 표본 3개와 코드·오프라인 실행의 대조.
- [PCAP 연계 설계](editorial/pcap-integration-plan.md): Suricata·Zeek 파일 분석을 기본으로, 폐쇄 veth 재생을 선택으로 구성.
- [검증 기록](editorial/verification.md): 실행한 검사와 아직 실행하지 않은 범위.

현재 원고는 **1~4장 초안**이다. [순차 집필 계획](editorial/sequential-authoring.md)에 따라 5~13장과 부록을 한 장씩 작성·검수·업로드한다. REV01과 1·2권 원고는 보존한다.

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

1장은 오프라인 파일 준비를 다룬다. 2장은 기존 kt66 환경의 전용 인덱스 `book3-r01-pilot01`에 85,306건을 적재하고 쿼리 14개와 실제 Wazuh UI를 확인했다. 기존 인덱스의 소멸·재생성·건수 감소는 없었다. 규칙·공용 템플릿·서비스를 변경하거나 공격·패킷 재생을 수행하지 않았다. 상세 범위는 [2장 검토 기록](editorial/chapter02-review.md)에 있다.

원본 `gen`은 같은 라운드 인덱스를 삭제 후 재생성하므로 공동 환경에서 바로 실행하지 않는다. 교재의 `load_dataset.py`는 파일 검사를 마친 뒤 새 전용 인덱스만 만들며, 이미 존재하는 인덱스에서는 중단한다. 로그 소멸이나 UUID·건수의 예상 밖 변동이 있으면 다른 작업이 끝날 때까지 기다린다.

## 재현과 자료

[저자용 재현 절차](editorial/reproduction.md)와 [자료 목록](editorial/source-register.md)을 참조한다. 실자료 원본·개별 식별자·PCAP·대용량 생성물·검수용 PDF는 이 저장소에 배포하지 않는다. 표본 통계와 출처·해시를 제공한다.

- 강의 코드: https://github.com/mrgrit/hack_ir_with_wazuh/tree/d6a2397fc31517147ddd09f58e0d153bc8cf0588/purple-agg
- 강의자료: https://drive.google.com/drive/folders/1opod1aNlgA9LW248K-U99VFK9QKBLiH6
- 실제 집계 표본: https://drive.google.com/drive/folders/1fJNfD402l9IRECphaDYX-Y6ca5VH7no0
