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

## 4. Falco 공격 시뮬레이션
Falco설치를 해봤으니 어떤식으로 이상 행위를 잡아내고 있는가 확인해보자.

새로운 Linux 터미널을 연다.

1. 실시간 로그 감시 (창 A | 이 창은 그대로 띄워두고 로그가 올라오는 걸 지켜보세요)

```
sudo journalctl –fu falco-modern-bpf
```

3. 컨테이너 침투 (창 B | 원래 쓰던 창)

```
sudo cat /etc/shadow
```

-> 입력 시 창B에서는 cups-browsed:!:19962::::::
hplip:!:19962::::::
gnome-remote-desktop:!*:19962:::::: 이런거 올라오고

창 A에서는 이런식으로 경고를 한다.

 3월 27 03:35:05 myj7378-Standard-PC-i440FX-PIIX-1996 falco[89251]: 03:35:05.162396887: Warning Sensitive file opened for reading by non-trusted program | file=/etc/shadow gparent=sudo ggparent=bash gggparent=sshd evt_type=openat user=root user_uid=0 user_loginuid=1000 process=cat proc_exepath=/usr/bin/cat parent=sudo command=cat /etc/shadow terminal=34818 container_id=host container_name=host container_image_repository= container_image_tag= k8s_pod_name=<NA> k8s_ns_name=<NA>

로그의 각 항목 설명

Warning Sensitive file opened for reading: "신뢰할 수 없는 프로그램이 민감한 파일(비밀번호 파일 등)을 읽으려고 시도함"이라는 탐지 결과입니다. 

file=/etc/shadow: 어떤 파일을 건드렸는지 명확히 보여줍니다. 

process=cat: 파일을 읽기 위해 사용된 명령어(프로세스)입니다. 

user=root: 이 명령어를 실행한 권한입니다. 

container_id=host: 현재는 호스트 환경에서 직접 실행된 것으로 인식되었거나, Falco 설정상 호스트 레벨의 위협으로 분류된 것입니다. 

evt_type=openat: 이게 가장 중요합니다! cat 명령어가 파일을 열기 위해 운영체제에 보낸 실제 시스템 콜 이름입니다. 
