# AutoEncoder 복원 오차 기반 이상치 탐지

## 전체 파이프라인
 
```
features_normal.csv
       │
       ├── 앞 80% ──────────────────────── X_train (학습)
       │                                       │
       │                               StandardScaler fit
       │                               + clip(-5, 5)
       │                                       │
       └── 뒤 20% ──┐                   AutoEncoder 학습
                    │                          │
scenario 정상 ──┤               복원 오차 계산 (train_errors)
scenario 공격 ──┤                          │
reverse_shell ─────┤            99.5th percentile → Threshold
crypto_mining ─────┘                          │
       │                               테스트셋 복원 오차
       └──── X_test ─────────────── (test_errors) → 이상치 판정
```

### AutoEncoder 아키텍처
 
```python
class AutoEncoder(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 16):
        super().__init__()
 
        def block(in_f, out_f, dropout=0.1):
            return [
                nn.Linear(in_f, out_f),
                nn.BatchNorm1d(out_f),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout) if dropout > 0 else nn.Identity()
            ]
 
        self.encoder = nn.Sequential(
            *block(input_dim, 256, 0.1),
            *block(256, 128, 0.1),
            *block(128, 64,  0.0),
            nn.Linear(64, latent_dim),          # bottleneck
        )
        self.decoder = nn.Sequential(
            *block(latent_dim, 64,  0.0),
            *block(64,  128, 0.1),
            *block(128, 256, 0.1),
            nn.Linear(256, input_dim),
        )
```
 
#### 구조 요약
 
```
[Encoder]                      [Decoder]
INPUT                          latent (16)
  → Linear(256) + BN + ReLU     → Linear(64)  + BN + ReLU
  → Linear(128) + BN + ReLU     → Linear(128) + BN + ReLU
  → Linear(64)  + BN + ReLU     → Linear(256) + BN + ReLU
  → Linear(16)  ← bottleneck    → Linear(INPUT)
```
 
| 설계 요소 | 선택 이유 |
|---|---|
| Dense(Fully-Connected) | 피처 순서에 구애받지 않아 다중 데이터셋에 robust |
| 점진적 압축 (256→128→64→16) | 정보 손실 최소화 |
| BatchNorm | 학습 안정성 향상 |
| Dropout(0.1) | 과적합 방지 |
| Sigmoid 미사용 | StandardScaler 출력이 [-5, 5] 범위이므로 불필요 |
| latent_dim=16 | 정상 패턴의 핵심 구조를 충분히 표현 가능한 크기 |
 
---

### 최종 성능 평가
 
**ROC-AUC: 0.9920**
 
| | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Normal | 1.00 | 0.99 | 0.99 | 6,970 |
| Attack | 0.79 | 0.97 | 0.87 | 313 |
| **Accuracy** | | | **0.99** | **7,283** |
| Macro avg | 0.90 | 0.98 | 0.93 | 7,283 |
| Weighted avg | 0.99 | 0.99 | 0.99 | 7,283 |
 
### 공격 유형별 탐지율
 
| 공격 유형 | 탐지 / 전체 | 탐지율 |
|---|---|---|
| scenario2 공격 | 25 / 25 | **100.0%** |
| scenario3 공격 | 26 / 26 | **100.0%** |
| scenario4 공격 | 25 / 25 | **100.0%** |
| scenario5 공격 | 25 / 25 | **100.0%** |
| reverse_shell | 138 / 148 | **93.2%** |
| crypto_mining | 64 / 64 | **100.0%** |
 
---
