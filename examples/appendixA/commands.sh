#!/usr/bin/env bash
# 본문의 실행 위치에서 한 명령씩 입력한다.

# C03-A-01 현재 저장소와 예제 위치를 확인한다.
pwd
ls manuscript/volume03-chapter13.docx
ls examples/chapter13/Q03-13-10.http

# C03-A-02 로컬 생성 자료가 보존됐는지 확인한다.
python3 tools/check_dataset.py build/r15-ch13

# C03-A-03 SSH 형식 원문 한 건을 읽는다.
python3 tools/inspect_events.py build/r15-ch13 \
  --decoder sshd --limit 1
