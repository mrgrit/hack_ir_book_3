# C03-01-12 | Ubuntu 분석 VM 터미널
# R01의 90일 학습 파일을 생성한다.
python3 tools/prepare_round.py \
  --source ~/hack_ir_with_wazuh_source/purple-agg \
  --round r01 --anchor 2026-11-01 \
  --days 90 --scale 0.005 \
  --run-id pilot01 --out build/r01-pilot01
