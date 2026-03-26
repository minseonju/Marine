## Autoencoder
기존 보안 도구(Falco)는 정답(Label)이 필요하지만, Autoencoder는 정상 데이터만을 학습

Autoencoder는 자기 자신을 복제하도록 훈련되는 신경망.

1. Encoder (압축): 입력된 시스콜 데이터의 핵심 특징만 남기고 크기를 줄입니다 (예: 10차원 → 2차원).
2. Decoder (복원): 압축된 정보를 다시 원래 크기로 되돌립니다 (예: 2차원 → 10차원).
3. 판단 기준 (Reconstruction Error):
 - 정상 데이터: 배운 대로 복원을 아주 잘함 → 에러 낮음 (정상 판정).
 - 공격 데이터: 배운 적 없는 패턴이라 복원을 못 함 → 에러 높음 (이상 판정).

간단한 Autoencoder 구현. 

```
import torch
import torch.nn as nn
import torch.optim as optim

# 1. 데이터 준비 (정상 데이터 숫자를 조금 줄여서 균형을 맞춤)
normal_data = torch.tensor([[1.0, 2.0, 1.0, 1.0], [1.1, 2.1, 0.9, 1.1]], dtype=torch.float32)
attack_data = torch.tensor([[5.0, 0.5, 0.1, 5.0]], dtype=torch.float32) # 확연히 다른 패턴

# 2. 모델 정의 (조금 더 깊게)
class PrototypeAE(nn.Module):
    def __init__(self):
        super(PrototypeAE, self).__init__()
        self.encoder = nn.Sequential(nn.Linear(4, 2), nn.ReLU())
        self.decoder = nn.Sequential(nn.Linear(2, 4), nn.ReLU())
    def forward(self, x):
        return self.decoder(self.encoder(x))

model = PrototypeAE()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.05)

# 3. 학습 (정상 데이터로 200번 반복 학습)
for epoch in range(200):
    optimizer.zero_grad()
    output = model(normal_data)
    loss = criterion(output, normal_data)
    loss.backward()
    optimizer.step()

# 4. 테스트 및 '이상 탐지' 로직
model.eval()
with torch.no_grad():
    n_out = model(normal_data[0])
    n_err = criterion(n_out, normal_data[0]).item()
    
    a_out = model(attack_data)
    a_err = criterion(a_out, attack_data).item()

    print(f"정상 복원 오류 (평균): {n_err:.4f}")
    print(f"공격 복원 오류: {a_err:.4f}")

    # 임계값 설정: 정상 에러의 3배 이상이면 공격으로 간주
    threshold = n_err * 3 
    if a_err > threshold:
        print(f"\n[!] 경고: 이상 점수({a_err:.4f})가 임계값({threshold:.4f})을 초과했습니다!")
        print(">>> 시스템 콜 패턴 분석 결과: '이상 행위(Anomaly)' 탐지됨")\
```

