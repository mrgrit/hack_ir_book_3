#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# C03-06-01 R06 파일을 생성한다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r06 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch06 --out build/r06-ch06

# C03-06-02 생성 파일의 건수·시간순·기간·해시를 검사한다.
python3 tools/check_dataset.py build/r06-ch06

# C03-06-03 검사한 자료를 새 전용 인덱스에 적재한다.
python3 tools/load_dataset.py build/r06-ch06 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure
