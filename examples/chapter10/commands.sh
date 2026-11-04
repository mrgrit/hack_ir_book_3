#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# C03-10-01 R10 파일을 생성한다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r10 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch10 --out build/r10-ch10

# C03-10-02 기간·시간순·건수·해시를 확인한다.
python3 tools/check_dataset.py build/r10-ch10

# C03-10-03 새 전용 인덱스에 적재한다.
python3 tools/load_dataset.py build/r10-ch10 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure
