#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# 5.1 선행 준비 — kt66 호스트

cd ~/hack_ir_book_3

git status --short

# 수정 중인 파일이 없을 때 갱신

git pull --ff-only

# C03-05-01 R05 이벤트 파일을 생성한다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r05 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch05 --out build/r05-ch05

# C03-05-02 생성 파일의 해시·기간·시간순·건수를 검사한다.
python3 tools/check_dataset.py build/r05-ch05

# C03-05-03 검사한 자료를 전용 인덱스에 적재한다.
python3 tools/load_dataset.py build/r05-ch05 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure
