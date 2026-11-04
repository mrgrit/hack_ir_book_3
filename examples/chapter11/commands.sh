#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# C03-11-01 R12를 로컬 파일로 만든다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r12 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch11 --out build/r12-ch11

# C03-11-02 R12의 기간·정렬·건수·해시를 확인한다.
python3 tools/check_dataset.py build/r12-ch11

# C03-11-03 R13을 별도 파일로 만든다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r13 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch11 --out build/r13-ch11

# C03-11-04 R13을 검사한다.
python3 tools/check_dataset.py build/r13-ch11

# C03-11-05 R12를 전용 인덱스에 적재한다.
python3 tools/load_dataset.py build/r12-ch11 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure

# C03-11-06 이어서 R13을 적재한다.
python3 tools/load_dataset.py build/r13-ch11 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure
