# LSTM-AE 기반 APT 탐지 모델

## 개요

컨테이너 환경에서 발생하는 시스템 콜 로그를  
시간 윈도우 기반 빈도 벡터로 변환하여  
LSTM 오토인코더(LSTM-AE)로 학습하는 비지도 이상 탐지 모델

- **역할** : 정상 패턴 학습 기반 APT 탐지
- **연관 모델** : CNN-AE (DaeYejun2)
- **수집 도구** : sysdig (eBPF 기반)

---

## 모델 구조

```
입력 시퀀스 (3, 95)
  ↓
[Encoder LSTM] 3층, hidden=64, dropout=0.2
  ↓
torch.flip() — 역순 변환
  ↓
[Decoder LSTM] 3층, hidden=95, dropout=0.2
  ↓
MSE 복원 오차 계산
  ↓
오차 > 임계값 → 이상(APT) 탐지
```

### 하이퍼파라미터

| 항목 | 설정값 |
|---|---|
| 입력 차원 | 95 (학습+테스트 syscall 합집합) |
| 시퀀스 길이 | 3 (1초 윈도우 × 3개) |
| hidden_dim | 64 |
| num_layers | 3 |
| dropout | 0.2 |
| 손실 함수 | MSELoss |
| 옵티마이저 | Adam (lr=0.0001, weight_decay=1e-5) |
| 스케줄러 | ReduceLROnPlateau (patience=10, factor=0.5) |
| Early Stopping | patience=20 |

---

## 전처리 방식

1. **1초 윈도우 분할** : `window_id = (ts_ns - ts_min) // 1e9`
2. **합집합 기준 벡터 생성** : 학습+테스트 syscall 합집합 (95종)
3. **비율 정규화** : `빈도 / (합계 + 1e-8)`
4. **슬라이딩 시퀀스 구성** : SEQ_WINDOW=3 → shape `(3, 95)`

---

## 데이터셋

### 프로토타입 : ADFA-LD

| 항목 | 내용 |
|---|---|
| 출처 | https://github.com/verazuo/a-labelled-version-of-the-ADFA-LD-dataset |
| 정상 학습 데이터 | Training_Data_Master: 22,956개 |
| 공격 테스트 데이터 | Attack_Data_Master: 24,708개 |
| 공격 유형 | Adduser, Hydra_FTP, Hydra_SSH, Java_Meterpreter, Meterpreter, Web_Shell |

### 실제 환경 데이터 (Sock Shop)

| 항목 | 내용 |
|---|---|
| 정상 학습 데이터 | raw_events.csv (Sock Shop 14개 컨테이너, 약 370만 행) |
| 시나리오 4 | raw_scenario4.csv (크립토마이닝) |
| 시나리오 5 | raw_scenario5.csv (리버스쉘) |
| M1 | raw_sockshop_m1.csv (약 6,800행) |
| M2 | raw_sockshop_m2.csv (약 117만 행) |
| Exfiltration | raw_data_exfiltration.csv (레이블 없음) |

---

## 실험 결과

### 프로토타입 : ADFA-LD

| 지표 | 값 |
|---|---|
| AUC-ROC | 0.6951 |
| Precision | 0.7931 |
| Recall | 0.4985 |
| F1-Score | 0.6122 |

### 실제 환경 데이터 — 시나리오별

| 시나리오 | AUC-ROC | Recall | Macro F1 | Falco 탐지율 |
|---|---|---|---|---|
| Scenario 4 (크립토마이닝) | 0.7311 | 73.8% | 0.7991 | 0% |
| Scenario 5 (리버스쉘) | 0.9910 | 95.9% | 0.9554 | 0% |

> Falco가 탐지하지 못한 Mimicry Attack에서 LSTM-AE 단독 탐지

### 실제 환경 데이터 — M1 / M2

| Data | Class | Precision | Recall | F1-Score |
|---|---|---|---|---|
| M1 | Normal | 29% | 50% | 36% |
| M1 | Attack | 56% | 33% | 42% |
| M2 | Normal | 77% | 92% | 84% |
| M2 | Attack | 95% | 86% | 90% |

> M1은 약 6,800행으로 정상 학습 데이터(약 370만 행) 대비 0.2% 수준으로 데이터 부족

### Exfiltration (레이블 없음)

| 전체 시퀀스 | 탐지 시퀀스 | 탐지율 |
|---|---|---|
| 20개 | 1개 | 5% |

---

## Falco 비교

| 시나리오 | Falco | LSTM-AE |
|---|---|---|
| Scenario 4 (크립토마이닝) | 0% | 73.8% |
| Scenario 5 (리버스쉘) | 0% | 95.9% |

---

## CNN-AE와의 역할 분담

| 항목 | CNN-AE (문예준) | LSTM-AE (임수환) |
|---|---|---|
| 탐지 방식 | 단기 이상 탐지 | 장기 패턴 탐지 |
| 역할 | 1차 필터 | 2차 검증 |

---

## 사용 방법

### 환경 설정

```bash
# Google Colab에서 실행 (T4 GPU 권장)
# 구글 드라이브에 데이터 업로드 필요
# raw_events.csv → /content/drive/MyDrive/
# raw_sockshop_m*.csv → /content/drive/MyDrive/
```

### 실행 순서 (LSTM_ae.ipynb)

```
셀 1: Google Drive 마운트
셀 2: 라이브러리 import & 전역 설정
셀 3: 데이터 로드 & 시퀀스 생성
셀 4: PyTorch 텐서 변환
셀 5: 모델 정의 & 학습
셀 6: 복원 오차 계산 & 임계값 탐색
셀 7: 결과 시각화
셀 8: 모델 저장
셀 9: 파일 다운로드
```

---

## 파일 구조

```
lstm/
├── LSTM_ADFA-LD_.ipynb          # ADFA-LD 프로토타입 실험
├── LSTM_ae.ipynb                # 실제 환경 최종 모델
├── LSTM_ae_exfiltration.ipynb   # 정답 레이블 x exfiltration 실험 
├── LSTM_ae_m1m2_combined.ipynb  # M1+M2 합산 실험
└── README.md
```

---

## 참고

- ADFA-LD 데이터셋: https://github.com/verazuo/a-labelled-version-of-the-ADFA-LD-dataset
- Falco: https://falco.org
- 프로젝트 GitHub: https://github.com/minseonju/Marine
