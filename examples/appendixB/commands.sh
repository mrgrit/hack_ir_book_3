#!/usr/bin/env bash
# 본문의 실행 위치에서 한 명령씩 입력한다.

# C03-B-01 현재 위치·교재 버전·기존 자료·새 출력 위치를 확인한다.
pwd
git rev-parse HEAD
python3 --version
ls build/r15-ch13/manifest.json
ls build/repro-b/r15-ch13

# C03-B-02 기존 생성 조건을 읽는다.
python3 -m json.tool build/r15-ch13/manifest.json

# C03-B-03 같은 조건으로 별도 로컬 자료를 생성한다.
python3 tools/prepare_round.py \
  --source ../hack_ir_with_wazuh_source/purple-agg \
  --round r15 --anchor 2026-11-01 --days 90 \
  --scale 0.005 --run-id ch13 \
  --out build/repro-b/r15-ch13

# C03-B-04 새 파일의 기간·정렬·건수·해시를 검사한다.
python3 tools/check_dataset.py build/repro-b/r15-ch13

# C03-B-05 원래 자료와 재생성 자료의 바이트를 대조한다.
sha256sum build/r15-ch13/events.bulk.ndjson \
  build/repro-b/r15-ch13/events.bulk.ndjson
sha256sum build/r15-ch13/manifest.json \
  build/repro-b/r15-ch13/manifest.json
