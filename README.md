  # Marine — 컨테이너 시스템 콜 기반 이상 탐지 (Container Syscall Anomaly
  Detection)

  <!-- 한 줄 소개: 이 프로젝트가 무엇을 하는지 1~2문장으로 채우기 -->
  컨테이너 환경에서 수집한 시스템 콜(syscall) 시퀀스를 학습하여 정상 행위와 공격
   행위를
  구분하는 이상 탐지(Anomaly Detection) 연구 프로젝트입니다.

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
  <!-- 채우기: 연구 배경/목적, 어떤 문제를 푸는지, 접근 방식(syscall 시계열 +
  AutoEncoder 계열) -->

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

  모델

  ┌─────────┬──────┬──────────────────┐
  │  모델   │ 설명 │ 성능(예: AUC/F1) │
  ├─────────┼──────┼──────────────────┤
  │ LSTM-AE │      │                  │
  ├─────────┼──────┼──────────────────┤
  │ CAE     │      │                  │
  └─────────┴──────┴──────────────────┘
