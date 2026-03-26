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

# 1. 데이터 준비
normal_data = torch.tensor([[1.0, 2.0, 1.0, 1.0], [1.1, 2.1, 0.9, 1.1]], dtype=torch.float32)
attack_data = torch.tensor([[5.0, 0.5, 0.1, 5.0]], dtype=torch.float32) # 확연히 다른 패턴

# 2. 모델 정의 (조금 더 깊게)
class PrototypeAE(nn.Module):
    def __init__(self):
        super(PrototypeAE, self).__init__()
        # 4개의 피쳐를 2개의 피쳐로 압축
        self.encoder = nn.Sequential(nn.Linear(4, 2), nn.ReLU())
        # 압축된 2개를 다시 원래의 4개로 복원
        self.decoder = nn.Sequential(nn.Linear(2, 4), nn.ReLU())
    def forward(self, x):
        return self.decoder(self.encoder(x))

model = PrototypeAE()
# MSE: 평균 제곱 오차. 정답(입력값)과 모델이 내뱉은 값(출력값)이 얼마나 유사한지 확인. (오차율이 클수록 점수가 낮다)
criterion = nn.MSELoss()
# Learning Rate 조절해주면서 내부 가중치 수정해주는 최적화 도구
optimizer = optim.Adam(model.parameters(), lr=0.05)

# 3. 학습 (정상 데이터로 200번 반복 학습)
for epoch in range(200):
    # 이전 학습의 기억을 지우고 새롭게 시작 -> 과거의 정보를 계속 이용하지 않기 위함
    optimizer.zero_grad()
    output = model(normal_data)
    loss = criterion(output, normal_data)
    # 역전파(출력값과 실제값의 차이(오차)를 기반으로, 출력층에서 입력층 방향으로 오차를 역전파하며 가중치(W)와 편향(b)을 업데이트하는 핵심 학습 알고리즘)
    loss.backward()
    # 추적된 에러를 바탕으로 모델을 계속 학습
    optimizer.step()

# 4. 테스트 및 '이상 탐지' 로직
model.eval()  # 학습이 끝났으니 테스트 모드로
with torch.no_grad():  # 평가할 때는 모델을 수정할 필요 없다.
    # 연산은 기록되지 않고 오로지 오차율 계산을 위한 평가만 진행(가중치 고정, Gradient 계산 X)
    n_out = model(normal_data[0])
    n_err = criterion(n_out, normal_data[0]).item()
    
    a_out = model(attack_data)
    a_err = criterion(a_out, attack_data).item()

    print(f"정상 복원 오류 (평균): {n_err:.4f}")
    print(f"공격 복원 오류: {a_err:.4f}")

    # 임계값 설정: 정상 에러의 3배 이상이면 공격으로 간주 -> 이 임계값 설정이 중요할 듯 합니다.
    threshold = n_err * 3 
    if a_err > threshold:
        print(f"\n[!] 경고: 이상 점수({a_err:.4f})가 임계값({threshold:.4f})을 초과했습니다!")
        print(">>> 시스템 콜 패턴 분석 결과: '이상 행위(Anomaly)' 탐지됨")\

# 출력 결과
# 정상 복원 오류 (평균): 0.7506
# 공격 복원 오류: 13.0526
# [!] 경고: 이상 점수(13.0526)가 임계값(2.2519)을 초과했습니다!
# >>> 시스템 콜 패턴 분석 결과: '이상 행위(Anomaly)' 탐지됨
```
