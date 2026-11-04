# 부록 A 검토 기록

2026-11-04 순차 집필. 13장 업로드(610aea9) 후 착수했다. 기존 1~13장 JSON·예제·검증 결과와 source mapping, OpenSearch Query DSL·Terms 공식 문서, Wazuh 규칙 문서를 대조했다.

query-index.csv는 조회 파일117개, command-index.csv는 본문 명령83개를 연결한다. 각 파일의 존재·명령 본문 일치·ID 유일성·원고 source SHA-256을 확인했다. 1장은 개별 C03-01-NN.sh이고 나머지 장은 commands.sh라는 차이를 반영했다. 2장 Q02는 _field_caps이며 본문 일반 코드 블록이므로 query 블록 수와 실제 조회 파일 수가 한 개 차이 난다.

R15 인덱스의 _count105293, _mapping의 date/keyword/long과 _meta.book3, 단일 문서 r15-000104075를 실제 읽기 전용으로 조회했다. PCAP 정규화 문서의 flow_id 문자열과 원본 EVE의 숫자를 구분했다. SSH 원문 추출 명령의 결과 ID r15-000000234를 확인했다. DQL 두 식은 13장의 검증된 후보 검색을 재사용했다. 새 적재·삭제·서비스·규칙 변경은 없었다.

B5 DOCX19쪽 전부를 개별 검수했다. flow_id 문장 수정 후4쪽, 참고자료 분리 후18·19쪽을 재검수하고 다른 지면의 픽셀 동일을 확인했다. 판형·테마·글꼴 세 종류·검정 문자·그림 해시·전체URL·명령/쿼리 파일 일치를 verify_appendix.py로 확인했다. Bash 구문을 통과했다. PDF는 검사용이며 배포하지 않는다.
