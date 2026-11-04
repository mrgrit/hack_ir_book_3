#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# C03-08-01 R08 파일을 만든다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r08 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch08 --out build/r08-ch08

# C03-08-02 시간순·기간·건수·해시를 검사한다.
python3 tools/check_dataset.py build/r08-ch08

# C03-08-03 검사한 파일을 전용 인덱스에 적재한다.
python3 tools/load_dataset.py build/r08-ch08 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure

# C03-08-04 전체 관측 구간의 개별 시간 간격을 계산한다.
python3 tools/flow_intervals.py build/r08-ch08 \
  --src 10.20.70.10 --dst 112.177.128.164 --port 443
