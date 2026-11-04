#!/usr/bin/env bash
# 복사용 명령 목록. 본문을 따라 한 명령씩 실행한다.

# C03-02-01 — 교재 도구가 있는 폴더로 이동한다.
cd ~/hack_ir_book_3

# C03-02-02 — 저장소에 수정 중인 파일이 있는지 확인한다.
git status --short

# C03-02-03 — 원격에 추가된 2장 도구를 가져온다.
git pull --ff-only

# C03-02-04 — 1장에서 생성한 파일의 해시·시간·건수를 다시 확인한다.
python3 tools/check_dataset.py build/r01-pilot01

# C03-02-05 — indexer 컨테이너의 내부 IP 주소를 확인한다.
sudo docker inspect \
  --format \
  '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  kt66-wazuh-indexer

# C03-02-06 — 검사가 끝난 데이터를 새 book3-r01-pilot01 인덱스에 적재한다.
python3 tools/load_dataset.py build/r01-pilot01 \
  --url https://10.20.32.110:9200 \
  --user admin --insecure
