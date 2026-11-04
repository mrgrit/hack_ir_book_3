#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# C03-13-01 R15 파일을 만든다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r15 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch13 --out build/r15-ch13

# C03-13-02 기간·순서·파일 해시를 검사한다.
python3 tools/check_dataset.py build/r15-ch13

# C03-13-03 검사한 자료를 새 전용 인덱스에 적재한다.
python3 tools/load_dataset.py build/r15-ch13 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure

# C03-13-04 같은 방향 연결의 인접 기록 간격을 계산한다.
python3 tools/flow_intervals.py build/r15-ch13 \
  --src 10.20.70.10 --dst 194.98.0.93 --port 443
