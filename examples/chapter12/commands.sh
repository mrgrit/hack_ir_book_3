#!/usr/bin/env bash
# 본문 순서와 실행 위치를 따라 한 명령씩 입력한다.

# C03-12-01 작업 위치·이미지·이름 중복을 확인한다.
pwd
sudo docker image inspect kt66-ips --format '{{.Id}}'
sudo docker ps -a --format '{{.Names}}'

# C03-12-02 새 분석 폴더와 관측 규칙을 준비한다.
mkdir build/pcap-work
WORK="$(pwd)/build/pcap-work"
mkdir "$WORK/input" "$WORK/config" "$WORK/rules"
mkdir "$WORK/output"
cp examples/chapter12/book3.rules "$WORK/rules/"

# C03-12-03 고정한 ZIP에서 PCAP 한 파일을 꺼낸다.
BASE_URL=https://www.malware-traffic-analysis.net/2025/01/22
curl -fL -o "$WORK/input/exercise.zip" \
  "$BASE_URL/2025-01-22-traffic-analysis-exercise.pcap.zip"
python3 tools/extract_pcap.py \
  "$WORK/input/exercise.zip" "$WORK/input/exercise.pcap" \
  --manifest examples/chapter12/dataset.json

# C03-12-04 패킷 수와 시각 범위를 기록한다.
python3 tools/inspect_pcap.py "$WORK/input/exercise.pcap" \
  > "$WORK/pcap-info.json"
cat "$WORK/pcap-info.json"

# C03-12-05 센서 설정 사본과 Zeek를 준비한다.
sudo docker cp \
  kt66-ips:/etc/suricata/suricata.yaml \
  "$WORK/config/suricata.yaml"
sudo docker pull zeek/zeek:8.0.0

# C03-12-06 전용 파일 분석 컨테이너를 만든 뒤 들어간다.
mkdir "$WORK/output/suri01"
sudo docker run -dit --name book3-suri-ch12 \
  --network none --cap-drop ALL \
  --security-opt no-new-privileges \
  --cpus 1 --memory 768m --user "$(id -u):$(id -g)" \
  --mount type=bind,src="$WORK",dst=/work,readonly \
  --mount type=bind,src="$WORK/output",dst=/output \
  --workdir /work --entrypoint /bin/bash kt66-ips
sudo docker inspect --format '{{.HostConfig.NetworkMode}}' \
  book3-suri-ch12
sudo docker exec -it book3-suri-ch12 /bin/bash

# C03-12-07 버전과 설정·규칙 문법을 확인한다.
suricata -V
suricata -T -c /work/config/suricata.yaml \
  -S /work/rules/book3.rules -l /output/suri01 \
  --set vars.address-groups.HOME_NET=[10.1.17.0/24] \
  --set unix-command.enabled=no

# C03-12-08 패킷을 전송하지 않고 EVE를 만든다.
suricata -r /work/input/exercise.pcap \
  -c /work/config/suricata.yaml \
  -S /work/rules/book3.rules -l /output/suri01 \
  --runmode single \
  --set vars.address-groups.HOME_NET=[10.1.17.0/24] \
  --set unix-command.enabled=no
exit

# C03-12-09 Suricata 분석을 마친 뒤 Zeek 작업 공간을 연다.
sudo docker stop book3-suri-ch12
mkdir "$WORK/output/zeek01"
sudo docker run -dit --name book3-zeek-ch12 \
  --network none --cap-drop ALL \
  --security-opt no-new-privileges \
  --cpus 1 --memory 768m --user "$(id -u):$(id -g)" \
  --mount type=bind,src="$WORK/input",dst=/input,readonly \
  --mount type=bind,src="$WORK/output/zeek01",dst=/output \
  --workdir /output --entrypoint /bin/bash zeek/zeek:8.0.0
sudo docker exec -it book3-zeek-ch12 /bin/bash

# C03-12-10 같은 PCAP를 Zeek로 분석한다.
zeek --version
zeek -r /input/exercise.pcap LogAscii::use_json=T
exit

# C03-12-11 반복 요청과 같은 실행의 연결을 대조한다.
sudo docker stop book3-zeek-ch12
python3 tools/compare_pcap_logs.py \
  --eve "$WORK/output/suri01/eve.json" \
  --http "$WORK/output/zeek01/http.log" \
  --conn "$WORK/output/zeek01/conn.log" \
  --source 10.1.17.215 --host 5.252.153.241 \
  --uri /1517096937

# C03-12-12 설정 비교 결과를 위한 새 출력 폴더를 준비한다.
mkdir "$WORK/output/suri-depth0"
sudo docker start book3-suri-ch12
sudo docker exec -it book3-suri-ch12 /bin/bash

# C03-12-13 재조립 깊이 제한만 바꿔 별도 분석한다.
suricata -r /work/input/exercise.pcap \
  -c /work/config/suricata.yaml \
  -S /work/rules/book3.rules -l /output/suri-depth0 \
  --runmode single \
  --set vars.address-groups.HOME_NET=[10.1.17.0/24] \
  --set unix-command.enabled=no \
  --set stream.reassembly.depth=0
exit

# C03-12-14 관측용 경보 원문을 준비하고 manager 터미널로 들어간다.
python3 tools/pcap_observations.py select \
  "$WORK/output/suri01/eve.json" --kind alert
sudo docker exec -it kt66-siem /bin/bash

# C03-12-15 복사한 JSON 한 줄의 분류를 확인한다.
/var/ossec/bin/wazuh-logtest

# C03-12-16 원문과 연결된 검색 자료를 만든다.
python3 tools/pcap_observations.py prepare \
  --eve "$WORK/output/suri01/eve.json" \
  --pcap-info "$WORK/pcap-info.json" \
  --config "$WORK/config/suricata.yaml" \
  --rules "$WORK/rules/book3.rules" \
  --sensor-version 6.0.4 --run-id ch12 \
  --out build/pcap-ch12
python3 tools/pcap_observations.py check build/pcap-ch12

# C03-12-17 새 전용 관측 인덱스에 적재한다.
python3 tools/pcap_observations.py load build/pcap-ch12 \
  --url https://10.20.32.110:9200 --user admin --insecure

# C03-12-18 독립 분석 VM의 도구와 이름 사용 여부를 확인한다.
sudo apt update
sudo apt install suricata iproute2 tcpreplay
suricata -V
tcpreplay --version
ip netns list
ip link show

# C03-12-19 송신·수신 네트워크 스택을 veth 한 쌍으로 잇는다.
sudo ip netns add b3-tx
sudo ip netns add b3-rx
sudo ip link add b3-tx0 type veth peer name b3-rx0
sudo ip link set b3-tx0 netns b3-tx
sudo ip link set b3-rx0 netns b3-rx
sudo ip netns exec b3-tx ip link set b3-tx0 up
sudo ip netns exec b3-rx ip link set b3-rx0 up
sudo ip netns exec b3-tx ip link show
sudo ip netns exec b3-rx ip link show
sudo ip netns exec b3-tx ip route show
sudo ip netns exec b3-rx ip route show

# C03-12-20 수신 센서를 먼저 실행한다.
cd ~/book3-pcap
mkdir output/live01
sudo ip netns exec b3-rx suricata \
  -i b3-rx0 -c config/suricata.yaml \
  -S rules/book3.rules -l output/live01

# C03-12-21 원래 간격의 1배로 한 번 전송한다.
cd ~/book3-pcap
sudo ip netns exec b3-tx tcpreplay \
  --intf1=b3-tx0 --multiplier=1 input/exercise.pcap
