# C03-01-14 | Ubuntu 분석 VM 터미널
# 웹 접근 이벤트의 원문과 필드를 확인한다.
python3 tools/inspect_events.py \
  build/r01-pilot01 \
  --decoder web-accesslog --limit 1
