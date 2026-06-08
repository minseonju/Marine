import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, confusion_matrix,
    classification_report, roc_curve, f1_score
)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy.stats import gaussian_kde
import warnings
warnings.filterwarnings('ignore')

torch.manual_seed(42)
np.random.seed(42)


print("=" * 60)
print("[ 1. 데이터 로드 ]")

normal_df    = pd.read_csv('features_normal.csv')
scenario2_df = pd.read_csv('sockshop_m1_features_labeled.csv')
scenario3_df = pd.read_csv('sockshop_m2_features_labeled.csv')
scenario4_df = pd.read_csv('features_data_exfiltration.csv')

# ── 공통 피처 추출 (전체 파일 교집합) ─────────────────────────
_drop = {'window_start_ns', 'total_events', 'label'}
normal_feats = set(normal_df.columns)
s2_feats     = set(scenario2_df.columns) - _drop
s3_feats     = set(scenario3_df.columns) - _drop
s4_feats     = set(scenario4_df.columns) - _drop


FEATURE_COLS = sorted(
    normal_feats & s2_feats & s3_feats & s4_feats
)
print(f"  공통 피처 수 : {len(FEATURE_COLS)}개")

# ── 시나리오별 정상 / 공격 분리 ───────────────────────────────
def split_normal_attack(df, cols):
    normal = df[df['label'] == 0][cols].values.astype(np.float32)
    attack = df[df['label'] == 1][cols].values.astype(np.float32)
    return normal, attack

s2_normal, s2_attack = split_normal_attack(scenario2_df, FEATURE_COLS)
s3_normal, s3_attack = split_normal_attack(scenario3_df, FEATURE_COLS)
s4_normal, s4_attack = split_normal_attack(scenario4_df, FEATURE_COLS)

def filter_empty_windows(arr):
    mask = (arr != 0).sum(axis=1) > 0
    return arr[mask]

s2_attack = filter_empty_windows(s2_attack)
s3_attack = filter_empty_windows(s3_attack)
s4_attack = filter_empty_windows(s4_attack)

print(f"  필터링 후 s2 공격 샘플 수: {len(s2_attack)}")  # 25 → 14 예상
print(f"  필터링 후 s3 공격 샘플 수: {len(s3_attack)}")
print(f"  필터링 후 s4 공격 샘플 수: {len(s4_attack)}")

print(f"  Normal (학습용) : {len(normal_df):,}개")
for name, n, a in [('scenario2', s2_normal, s2_attack),
                   ('scenario3', s3_normal, s3_attack),
                   ('scenario4', s4_normal, s4_attack)]:
    print(f"  {name}  정상/공격 : {len(n)}/{len(a)}개")


print("\n[ 2. 학습/테스트 분리 ]")

all_normal  = normal_df[FEATURE_COLS].values.astype(np.float32)
n_train     = int(len(all_normal) * 0.8)
X_train     = all_normal[:n_train]
normal_test = all_normal[n_train:]

# ── 테스트셋: 정상은 features_normal 20%만, 공격은 시나리오 전체 ──
X_test = np.vstack([
    normal_test,
    s2_attack, s3_attack, s4_attack,
])

n_norm = len(normal_test)
n_atk  = (len(s2_attack) + len(s3_attack)
         + len(s4_attack))
y_test = np.concatenate([np.zeros(n_norm), np.ones(n_atk)])

# ── 공격 유형별 마스크 ─────────────────────────────────────────
offset = n_norm
def make_mask(total, start, length):
    m = np.zeros(total, dtype=bool)
    m[start:start + length] = True
    return m
total  = len(y_test)
s2_mask = make_mask(total, offset, len(s2_attack)); offset += len(s2_attack)
s3_mask = make_mask(total, offset, len(s3_attack)); offset += len(s3_attack)
s4_mask = make_mask(total, offset, len(s4_attack)); offset += len(s4_attack)
attack_mask = y_test == 1
normal_mask = y_test == 0

print(f"  정상 (features_normal 20%) : {n_norm}개")
print(f"  공격 (s2+s3+s4)         : {n_atk}개")
print(f"  테스트 합계                 : {total}개")


print("\n[ 3. 전처리 ]")

scaler     = StandardScaler()
X_train_sc = np.clip(scaler.fit_transform(X_train), -5, 5).astype(np.float32)
X_test_sc  = np.clip(scaler.transform(X_test),      -5, 5).astype(np.float32)

X_train_t  = torch.FloatTensor(X_train_sc)
X_test_t   = torch.FloatTensor(X_test_sc)
train_loader = DataLoader(TensorDataset(X_train_t), batch_size=256, shuffle=True)

print(f"  X_train : {X_train_sc.shape}  →  스케일링 + clip(-5,5) 완료")
print(f"  X_test  : {X_test_sc.shape}")


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
            nn.Linear(64, latent_dim),
        )
        self.decoder = nn.Sequential(
            *block(latent_dim, 64,  0.0),
            *block(64,  128, 0.1),
            *block(128, 256, 0.1),
            nn.Linear(256, input_dim),
            # StandardScaler 출력은 [-5,5] 범위이므로 Sigmoid 미사용
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

    @torch.no_grad()
    def recon_error(self, x: torch.Tensor, mode='mse') -> np.ndarray:
        self.eval()
        x = x.to(next(self.parameters()).device)
        residual = (x - self(x)) ** 2
        if mode == 'mse':
            return residual.mean(dim=1).cpu().numpy()
        elif mode == 'max':
            return residual.max(dim=1).values.cpu().numpy()
        elif mode == 'range':
            return (residual.max(dim=1).values - residual.min(dim=1).values).cpu().numpy()
        elif mode == 'topk':
            return torch.topk(residual, 10, dim=1).values.mean(dim=1).cpu().numpy()


device     = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
INPUT_DIM  = len(FEATURE_COLS)
LATENT_DIM = 16
EPOCHS     = 50

model     = AutoEncoder(INPUT_DIM, LATENT_DIM).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', patience=10, factor=0.5
)
criterion = nn.MSELoss()

print(f"\n[ 4. 모델 정보 ]")
print(f"  Device    : {device}")
print(f"  Input dim : {INPUT_DIM}  |  Latent dim : {LATENT_DIM}")
print(f"  Params    : {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")


print("\n[ 5. 학습 시작 ]")
train_losses = []

for epoch in range(1, EPOCHS + 1):
    model.train()
    ep_loss = 0.0
    for (x,) in train_loader:
        x = x.to(device)
        optimizer.zero_grad()
        loss = criterion(model(x), x)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        ep_loss += loss.item()

    avg = ep_loss / len(train_loader)
    train_losses.append(avg)
    scheduler.step(avg)

    if epoch % 10 == 0:
        lr_now = optimizer.param_groups[0]['lr']
        print(f"  Epoch [{epoch:3d}/{EPOCHS}]  Loss: {avg:.6f}  LR: {lr_now:.2e}")

print("  학습 완료!")


print("\n[ 6. 복원 오차 계산 ]")

MODE = 'mse'  # 'mse' / 'max' / 'range' / 'topk' 교체하면서 실행
train_errors = model.recon_error(X_train_t, mode=MODE)
test_errors  = model.recon_error(X_test_t,  mode=MODE)

print(f"  Train 오차 | mean: {train_errors.mean():.5f}  std: {train_errors.std():.5f}")
print(f"  Test  오차 | mean: {test_errors.mean():.5f}  std: {test_errors.std():.5f}")
print(f"\n  [공격 유형별 오차]")
for name, mask in [('scenario2 공격', s2_mask), ('scenario3 공격', s3_mask),
                   ('scenario4 공격', s4_mask),]:
    e = test_errors[mask]
    if len(e) > 0:
        print(f"  {name:<18} | mean: {e.mean():.5f}  std: {e.std():.5f}")


print("\n[ 7. 임계값 설정 (순수 비지도 방식) ]")

THRESHOLD_PCT = 99.8
best_thr      = np.percentile(train_errors, THRESHOLD_PCT)
y_pred        = (test_errors >= best_thr).astype(int)

print(f"  임계값 (train {THRESHOLD_PCT}th percentile) : {best_thr:.5f}")


print("\n" + "=" * 60)
print("[ 8. 최종 성능 평가 ]")

roc_auc = roc_auc_score(y_test, test_errors)
print(f"\n  ROC-AUC : {roc_auc:.4f}\n")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

print("  [공격 유형별 탐지율]")
for name, mask in [('scenario2 공격', s2_mask), ('scenario3 공격', s3_mask),
                   ('scenario4 공격', s4_mask)]:
    if mask.sum() == 0:
        continue
    det   = int(((y_pred == 1) & mask).sum())
    total = int(mask.sum())
    bar   = '█' * int((det / total * 100) // 5)
    print(f"    {name:<18}: {det:3d}/{total}  ({det/total*100:5.1f}%)  {bar}")


fig = plt.figure(figsize=(20, 10))
gs  = gridspec.GridSpec(2, 4, figure=fig, hspace=0.4, wspace=0.35)

# ── (1) 학습 손실 곡선 ────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(train_losses, color='steelblue', linewidth=1.5)
ax1.set_title('Training Loss Curve', fontweight='bold')
ax1.set_xlabel('Epoch'); ax1.set_ylabel('MSE Loss')
ax1.grid(alpha=0.3)

# ── (2) 복원 오차 분포 (KDE) ──────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
sc_all_attacks = np.concatenate([test_errors[s2_mask], test_errors[s3_mask],
                                  test_errors[s4_mask]])
groups = {
    'Normal'           : test_errors[normal_mask],
    'Scenario Attacks' : sc_all_attacks,
}
colors  = ['royalblue', 'orange', 'tomato', 'purple']
x_range = np.linspace(0, np.percentile(test_errors, 99.5), 500)
for (name, errs), color in zip(groups.items(), colors):
    if len(errs) >= 2:
        kde = gaussian_kde(errs, bw_method=0.3)
        ax2.plot(x_range, kde(x_range),
                 label=f'{name} (n={len(errs)})', color=color, linewidth=2)
ax2.axvline(best_thr, color='black', linestyle='--', linewidth=1.5,
             label=f'Threshold={best_thr:.5f}')
ax2.set_title('Reconstruction Error Distribution', fontweight='bold')
ax2.set_xlabel('MSE'); ax2.set_ylabel('Density')
ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

# ── (3) ROC Curve ─────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
fpr, tpr, _ = roc_curve(y_test, test_errors)
ax3.plot(fpr, tpr, color='darkorange', linewidth=2, label=f'AUC={roc_auc:.4f}')
ax3.fill_between(fpr, tpr, alpha=0.1, color='darkorange')
ax3.plot([0, 1], [0, 1], 'k--', linewidth=0.8)
ax3.set_title('ROC Curve', fontweight='bold')
ax3.set_xlabel('FPR'); ax3.set_ylabel('TPR')
ax3.legend(); ax3.grid(alpha=0.3)

# ── (4) 공격 유형별 탐지율 바 차트 ───────────────────────────
ax4 = fig.add_subplot(gs[0, 3])
named_masks = [
    ('s2',          s2_mask),
    ('s3',          s3_mask),
    ('s4',          s4_mask),
    ('Total\nAttack',  attack_mask),
]
valid = [(n, m) for n, m in named_masks if m.sum() > 0]
cat_names  = [n for n, m in valid]
recalls    = [((y_pred == 1) & m).sum() / m.sum() * 100 for n, m in valid]
bar_colors = ['steelblue' if r >= 70 else 'tomato' for r in recalls]
bars = ax4.bar(cat_names, recalls, color=bar_colors, edgecolor='white', width=0.6)
for bar, r in zip(bars, recalls):
    ax4.text(bar.get_x() + bar.get_width() / 2, r + 1.5,
             f'{r:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax4.set_ylim(0, 120); ax4.set_ylabel('Detection Rate (%)')
ax4.set_title('Attack Detection Rate by Type', fontweight='bold')
ax4.tick_params(axis='x', labelsize=8)
ax4.grid(alpha=0.3, axis='y')

# ── (5) Confusion Matrix ──────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 0:2])
cm_mat = confusion_matrix(y_test, y_pred)
sns.heatmap(cm_mat, annot=True, fmt='d', cmap='Blues', ax=ax5,
            xticklabels=['Pred Normal', 'Pred Attack'],
            yticklabels=['Actual Normal', 'Actual Attack'],
            annot_kws={'size': 14})
ax5.set_title('Confusion Matrix (전체)', fontweight='bold')

# ── (6) 임계값 퍼센타일 곡선 (train only — y_test 미사용) ─────
ax6 = fig.add_subplot(gs[1, 2:4])
pcts = np.arange(80, 100.5, 0.5)
thrs = [np.percentile(train_errors, p) for p in pcts]
ax6.plot(pcts, thrs, color='steelblue', linewidth=2)
ax6.axvline(THRESHOLD_PCT, color='tomato', linestyle='--', linewidth=2,
             label=f'{THRESHOLD_PCT}th pct → {best_thr:.5f}')
ax6.set_title('Threshold by Percentile (train only, no data leakage)',
              fontweight='bold')
ax6.set_xlabel('Percentile'); ax6.set_ylabel('Threshold Value')
ax6.legend(); ax6.grid(alpha=0.3)

plt.suptitle('Unified AutoEncoder — All Attack Types Detection Results',
             fontsize=13, fontweight='bold')
plt.savefig('ae_unified_results.png', dpi=150, bbox_inches='tight')
plt.show()
print("\n결과 저장: ae_unified_results.png")

