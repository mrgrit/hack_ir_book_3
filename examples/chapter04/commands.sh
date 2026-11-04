#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# 4.1 선행 준비 — kt66 호스트

cd ~/hack_ir_book_3

git status --short

# 수정 중인 파일이 없을 때 갱신

git pull --ff-only

# C03-04-01 R03 자료를 새 폴더에 생성한다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r03 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch04 --out build/r03-ch04

# C03-04-02 R03의 해시·기간·순서·건수를 검사한다.
python3 tools/check_dataset.py build/r03-ch04

# C03-04-03 R03 검사를 마친 뒤 R04 자료를 생성한다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r04 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch04 --out build/r04-ch04

# C03-04-04 R04 파일을 검사한다.
python3 tools/check_dataset.py build/r04-ch04

# C03-04-05 검사한 R03을 새 인덱스에 적재한다.
python3 tools/load_dataset.py build/r03-ch04 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure

# C03-04-06 R03 적재 확인 후 R04를 적재한다.
python3 tools/load_dataset.py build/r04-ch04 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure
