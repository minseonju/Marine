  # Marine — 컨테이너 시스템 콜 기반 이상 탐지 (Container Syscall Anomaly Detection)

  <!-- 한 줄 소개: 이 프로젝트가 무엇을 하는지 1~2문장으로 채우기 -->
  컨테이너 환경에서 수집한 시스템 콜(syscall) 시퀀스를 학습하여 정상 행위와 공격
   행위를
  구분하는 이상 탐지(Anomaly Detection) 연구 프로젝트입니다.

  본 프로젝트는 Sock Shop 마이크로서비스 환경에서 정상 트래픽을 수집하고,
Reverse Shell, Crypto Mining, Data Exfiltration 등의 공격 데이터와 비교하여
AutoEncoder 기반 이상 탐지 모델의 탐지 가능성을 평가합니다.


  ## 목차
  - [개요](#개요)
  - [데이터셋](#데이터셋)
  - [공격 시나리오](#공격-시나리오)
  - [전처리 파이프라인](#전처리-파이프라인)
  - [모델](#모델)
  - [디렉터리 구조](#디렉터리-구조)
  - [사용법](#사용법)
  - [팀](#팀)

  ## 개요
클라우드 및 마이크로서비스 환경에서 APT(Advanced Persistent Threat)와 같은
정교한 공격은 정상 프로세스를 위장하여 기존 룰 기반 탐지 도구를 우회하는 경우가 많다.

본 프로젝트는 Sock Shop 마이크로서비스 컨테이너 환경에서 sysdig로 수집한
syscall 시계열 데이터를 기반으로, AutoEncoder 계열 비지도 학습 모델을 활용하여
레이블 없이도 정상 패턴을 학습하고 이상 행위를 탐지하는 시스템을 구현한다.

- 수집: `sysdig`를 이용해 컨테이너 단위 system call 수집
- 전처리: syscall 빈도 기반 histogram feature와 syscall 순서 기반 N-gram feature 생성
- 학습: 정상 데이터만 사용하여 AutoEncoder 학습
- 탐지: 입력 데이터를 복원했을 때 발생하는 reconstruction error를 기준으로 이상 여부 판단
- 비교: Falco와 같은 rule 기반 런타임 보안 도구와 탐지 결과 비교

  ## 데이터셋
  수집 환경과 라벨링 체계는 다음과 같습니다.

  | 항목 | 내용 |
  |---|---|
  | 수집 도구 | sysdig (호스트 레벨, 컨테이너 필터링) |
  | 대상 환경 | KVM VM / Sock Shop 마이크로서비스 |
  | 윈도우 | 5초 단위 |
  | 특성 | unigram + bigram + trigram + process (327차원) |
  | 라벨 | 0 = 정상(Normal), 1 = 공격(Attack) |

  - **raw 데이터**: `ts_ns, syscall, proc_name, tid, evt_cpu, label`
  - **전처리 데이터**: `window_start_ns, total_events, label` + 327개 특성 컬럼
  <!-- 채우기: 각 데이터 파일이 어떤 시나리오/수집조건인지 표로 정리 -->

  ## 공격 시나리오
  | 시나리오 | 설명 | 수집 스크립트 |
  |---|---|---|
  | Reverse Shell (bash/python3/php/perl/ruby/socat/nc 등) | <!-- 채우기 --> |
  `run_scenario*.sh` |
  | Crypto Mining | <!-- 채우기 --> | <!-- 채우기 --> |
  | Command Injection | <!-- 채우기 --> | `run_scenario5.sh` |
  | Environment Variable Injection | <!-- 채우기 --> | `run_scenario4.sh` |
  | Data Exfiltration | <!-- 채우기: 정찰→수집→DB덤프→유출→흔적제거 --> | <!--
  채우기 --> |
  | Sock Shop (method1/method2) | <!-- 채우기 --> | `run_sockshop_method*.sh` |

  ## 전처리 파이프라인
  <!-- 채우기: vocab.json 역할, 5초 윈도우 분할, n-gram 빈도 정규화, 라벨링 방식
   -->
  ```bash
  python3 attack_dataset/preprocess_pipeline.py   # 예시: 실제 사용법으로 수정

## 모델

| 모델 | 설명 | 성능(AUC/F1) |
|------|------|-------------|
| LSTM-AE | 입력: 시스템콜 실행 시퀀스. 탐지: 비정상적 순서 패턴 포착. | F1 score: 0.85 |
| AE | 입력: 시간 window별 시스템콜 빈도 벡터. 탐지: 비정상적 빈도 급증 포착. | F1 score: 0.89 |

## 디렉터리 구조

프로젝트의 주요 파일 및 디렉터리 구성은 다음과 같습니다.

```text
Marine/
├── Tutorial/                         # 프로젝트 실행 및 실습 관련 자료
├── attack_dataset/                   # 공격 데이터셋 및 전처리 파이프라인
│   ├── raw_attack/                   # 원시 syscall 로그 CSV
│   ├── preprocessed_attack/          # 전처리된 특성 데이터(CSV, NPY)
│   ├── pipeline/                     # 데이터 처리 파이프라인 관련 파일
│   ├── scenarios/                    # 공격 시나리오 관련 파일
│   └── preprocess_pipeline.py        # 공격 데이터 전처리 스크립트
├── model/                            # 이상 탐지 모델 코드
│   ├── AE_model/                     # AutoEncoder 기반 모델
│   ├── lstm/                         # LSTM 기반 모델
│   └── text.md                       # 모델 관련 메모/문서
├── scripts/                          # 공격 및 Sock Shop 실행 스크립트
│   ├── run_scenario2.sh
│   ├── run_scenario3.sh
│   ├── run_scenario4.sh
│   ├── run_scenario5.sh
│   ├── run_sockshop_method1.sh
│   └── run_sockshop_method2.sh
├── scaler.pkl                        # 전처리/정규화에 사용된 scaler 객체
├── vocab.json                        # syscall 및 feature vocabulary
└── README.md                         # 프로젝트 설명 문서
```

각 디렉터리의 역할은 다음과 같습니다.

| 경로 | 설명 |  
|---|---|  
| `Tutorial/` | 프로젝트 실행 또는 실습 과정에서 사용하는 자료 |  
| `attack_dataset/raw_attack/` | sysdig 등으로 수집한 원시 syscall 로그 CSV |  
| `attack_dataset/preprocessed_attack/` | 모델 입력용으로 전처리된 CSV/NPY 특성 데이터 |  
| `attack_dataset/preprocess_pipeline.py` | raw attack 로그를 모델 입력 형식으로 변환하는 전처리 스크립트 |  
| `model/AE_model/` | AutoEncoder 기반 이상 탐지 모델 |  
| `model/lstm/` | LSTM 기반 이상 탐지 모델 |  
| `scripts/` | 공격 시나리오 및 Sock Shop 데이터 수집 실행 스크립트 |  
| `scaler.pkl` | 학습/추론 시 동일한 스케일링을 적용하기 위한 객체 |  
| `vocab.json` | syscall 및 n-gram feature 매핑 정보 |  

## 사용법

  ### 1) 데이터 수집 (VM에서)  
  `bash run_scenarioN.sh`  
  ### 2) 전처리  
  `python3 attack_dataset/preprocess_pipeline.py --scenario N`  
  ### 3) 모델 학습/평가  
  모델 폴더의 ipynb 확인

## 팀
| 이름 | 역할 | 담당 업무 | GitHub |
|---|---|---|---|
| 백하준 | 팀장 | 프로젝트 기획, 서버환경 구현 | [@KIMGEEK](https://github.com/KIMGEEK) |
| 민선주 | 데이터 전처리 | 샘플데이터 수집, 데이터 전처리, 공격 시나리오 구현 | [@minseonju](https://github.com/minseonju) |
| 임수환 | 모델 개발 | LSTM-AE / AE 모델 학습 및 평가 (시계열) | [@limlimsu](https://github.com/limlimsu) |
| 문예준 | 모델 개발 | LSTM-AE / AE 모델 학습 및 평가 () | [@DaeYejun2](https://github.com/DaeYejun2) |
