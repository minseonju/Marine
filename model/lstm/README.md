# LSTM-AE 기반 APT 탐지 모델 

## 개요
컨테이너 환경에서 발생하는 시스템 콜 시퀀스를
LSTM 오토인코더(LSTM-AE)로 학습하여
장기 지속 위협(APT)을 탐지하는 비지도 학습 모델

- 역할 : 장기 패턴 기반 APT 탐지
- 연관 모델 : CNN-AE
  
---

## 모델 구조 
입력 시퀀스 (syscall 100개)
↓
[LSTM Encoder] → 128차원 벡터로 압축
↓
[LSTM Decoder] → 원본 시퀀스 복원
↓
Reconstruction Error 계산
↓
임계값 초과 시 APT 경보

---

## 데이터셋

### 프로토타입 : ADFA-LD
| 항목 | 내용 |
|---|---|
| 출처 | https://github.com/verazuo/a-labelled-version-of-the-ADFA-LD-dataset |
| 정상 학습 데이터 | Training_Data_Master: 22,956개 |
| 공격 테스트 데이터 | Attack_Data_Master: 24,708개 |
| 공격 유형 | Adduser, Hydra_FTP, Hydra_SSH, Java_Meterpreter, Meterpreter, Web_Shell |

### 실제 환경 데이터 
| 항목 | 내용 |
|---|---|
| 정상 데이터 | raw_events.csv (Sock Shop 컨테이너 14개) |
| 공격 데이터 | raw_attack (리버스셸 7가지) |
| 수집 도구 | sysdig |

---

## 실험 결과 

### ADFA-LD 프로토타입
| 지표 | 값 |
|---|---|
| AUC-ROC | 0.6951 |
| Precision | 0.7931 |
| Recall | 0.4985 |
| F1-Score | 0.6122 |
| FPR | 0.1400 |

### 실제 환경 데이터
| 지표 | 값 |
|---|---|
| AUC-ROC | 0.9008 |
| Precision | 0.9665 |
| Recall | 0.8385 |
| F1-Score | 0.8980 |
| FPR | 0.0100 |

### 공격 유형별 탐지율 (실제 데이터)
| 공격 유형 | 탐지율 |
|---|---|
| rs_ncmkfifo | 87.6% |
| rs_python3 | 87.0% |
| rs_bash_post | 86.9% |
| rs_perl_post | 85.1% |
| rs_ruby | 83.8% |
| rs_php | 82.9% |
| rs_socat | 78.8% |

---

## CNN-AE와의 역할 분담

| 항목 | CNN-AE (문예준) | LSTM-AE (임수환) |
|---|---|---|
| 입력 | 3-gram 피처 벡터 | raw syscall 시퀀스 |
| 탐지 방식 | 단기 이상 탐지 | 장기 패턴 탐지 |
| Recall | 0.91 | 0.84 |
| Precision | 0.11 | 0.97 |
| 역할 | 1차 필터 | 2차 검증 |

---

## 사용 방법

### 환경 설정
```bash
# Google Colab에서 실행
# 구글 드라이브에 데이터 업로드 필요
# raw_events.csv → /content/drive/MyDrive/
# raw_attack/ → /content/drive/MyDrive/raw_attack/
```

### 실행 순서

LSTM_raw_dataset.ipynb 열기
런타임 → T4 GPU 설정
셀 순서대로 실행
셀 1: 드라이브 마운트
셀 2: Config 설정
셀 3: 데이터 전처리
셀 4: 정규화 + 텐서 변환
셀 5: 모델 학습
셀 6: 성능 평가
셀 7: 시각화 + 저장

---

## 파일 구조
lstm_ae/
├── LSTM_ADFA-LD.ipynb       # ADFA-LD 프로토타입 실험
├── LSTM_raw_dataset.ipynb   # 실제 데이터 학습
├── README.md
└── model/
├── lstm_ae.pth          # 학습된 모델 가중치
├── scaler.pkl           # 정규화 기준값
└── threshold.npy        # 탐지 임계값

---

## 참고
- ADFA-LD 데이터셋: https://github.com/verazuo/a-labelled-version-of-the-ADFA-LD-dataset
- Falco: https://falco.org
- 프로젝트 GitHub: https://github.com/minseonju/Marine
