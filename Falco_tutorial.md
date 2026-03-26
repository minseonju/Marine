# Falco 튜토리얼

## 1. 환경 구축
Falco는 커널 모듈이나 eBPF를 사용하므로 가급적 리눅스 환경에서 진행

Docker 설치: Nginx + Python 샌드박스 환경 이용

Falco 설치: 공식 저장소를 추가하여 apt로 간편하게 설치할 수 있습니다.

필수 도구 설치: 시스템 콜을 관찰하기 위한 strace와 컨테이너 환경인 docker, docker-compose를 설치

```
sudo apt update && sudo apt install -y strace docker.io docker-compose

# 간단한 명령어가 실행될 때 OS 내부에서 어떤 시스템 콜들이 호출되는지 확인 (굳이 안해봐도 될거 같음;)
strace ls
```

## 2. Docker 환경 구축
Nginx + Python 샌드박스 환경 이용. 2개의 컨테이너만 띄워 시스템 콜 관찰 가능

nano docker-compose.yml

docker-compose.yml 파일 안에 아래 코드를 치면 됨

```
services:
  web-server:
    image: nginx:latest  # 웹 서버 (정상 동작 담당)
    ports:
      - "8080:80"

  attacker-sim:
    image: python:3.10-slim  # 공격 시뮬레이션용 (예준 님의 실험용)
    tty: true
```

docker compose 플러그인 설치
sudo apt update
sudo apt install –y docker-compose-v2

docker compose up –d

관리자 권한으로 실행
sudo docker compose up –d

sudo docker ps를 쳤을 때 web-server와 attacker-sim이 목록에 나오면 환경 구축은 끝

| names | image | status |
| --- | --- | --- |
| web-server | nginx:latest | Up (Running) |
| attacker-sim | python:3.10-slim | Up (Running) |

만약 나오지 않는다면 제미나이에게 물어보자..


## 3. Falco 설치

sudo apt install –y curl

Falco 신뢰 키 추가

```
curl -fsSL https://falco.org/repo/falcosecurity-packages.asc | sudo gpg --dearmor –o /usr/share/keyrings/falco-archive-keyring.gpg
```

저장소 리스트 추가

```
echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] https://download.falco.org/packages/deb stable main" | sudo tee /etc/apt/sources.list.d/falcosecurity.list
```

드디어 Falco 설치
```
sudo apt update
sudo apt install –y falco
```

설치 확인
```
sudo systemctl status falco
```

<img width="458" height="186" alt="image" src="https://github.com/user-attachments/assets/cfc3a0a4-66cd-4b07-ab6c-f78a32692d6f" />

이렇게 뜨면 성공!!!!!🎇🎇









