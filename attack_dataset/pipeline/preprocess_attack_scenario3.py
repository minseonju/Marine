import json, os
import numpy as np
import pandas as pd

ATTACK_FILE   = "/home/marine/attack_data/scenario3_raw.json"
TIMELINE_FILE = "/home/marine/attack_data/timeline_scenario3.txt"
VOCAB_FILE    = "/home/marine/vocab.json"
OUTPUT_DIR    = "/home/marine/attack_data/preprocessed_scenario3"
CONTAINER_ID  = "e5c241b5cfb0"
WINDOW_SEC    = 5
NS_PER_SEC    = 1_000_000_000

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. vocab 로드
print("[1] vocab.json 로드 중...")
with open(VOCAB_FILE) as f:
    vocab_raw = json.load(f)

vocab = {
    "syscalls": vocab_raw["syscalls"],
    "bigrams":  [tuple(b) for b in vocab_raw["bigrams"]],
    "trigrams": [tuple(t) for t in vocab_raw["trigrams"]],
    "procs":    vocab_raw["procs"],
}
n_sc   = len(vocab["syscalls"])
n_bg   = len(vocab["bigrams"])
n_tg   = len(vocab["trigrams"])
n_proc = len(vocab["procs"])
n_feat = n_sc + n_bg + n_tg + n_proc

# vocab 기반 열 이름 생성 (기존 preprocess.py 방식과 동일)
feature_names = (
    [f"sc_{sc}"        for sc in vocab["syscalls"]] +
    [f"bg_{a}_{b}"     for a, b in vocab["bigrams"]] +
    [f"tg_{a}_{b}_{c}" for a, b, c in vocab["trigrams"]] +
    [f"proc_{p}"       for p in vocab["procs"]]
)
print(f"   특성 차원: {n_sc}+{n_bg}+{n_tg}+{n_proc} = {n_feat}")

sc_idx   = {sc: i for i, sc in enumerate(vocab["syscalls"])}
bg_idx   = {bg: i for i, bg in enumerate(vocab["bigrams"])}
tg_idx   = {tg: i for i, tg in enumerate(vocab["trigrams"])}
proc_idx = {p:  i for i, p  in enumerate(vocab["procs"])}

# 2. 타임라인 로드
print("[2] 타임라인 로드 중...")
timeline = {}
with open(TIMELINE_FILE) as f:
    for line in f:
        key, val = line.strip().split(": ")
        timeline[key] = int(val)

t_normal_start = timeline["NORMAL_START"]
t_attack_start = timeline["ATTACK_START"]
t_attack_end   = timeline["ATTACK_END"]
print(f"   정상 구간 시작: {t_normal_start}")
print(f"   공격 구간 시작: {t_attack_start}")

# 3. JSON 파싱 (victim 컨테이너만)
print("[3] JSON 파싱 중...")
events = []
with open(ATTACK_FILE) as f:
    for line in f:
        line = line.strip()
        if not line or CONTAINER_ID not in line:
            continue
        try:
            ev = json.loads(line)
            events.append({
                "ts_ns":   int(ev["evt.outputtime"]),
                "syscall": ev.get("evt.type", "unknown").lower().strip(),
                "proc":    ev.get("proc.name", "unknown").lower().strip(),
            })
        except:
            continue

print(f"   victim 이벤트: {len(events)}개")
events.sort(key=lambda x: x["ts_ns"])

# 4. 윈도우 특성 추출
print("[4] 윈도우 특성 추출 중...")
window_ns  = WINDOW_SEC * NS_PER_SEC
ts_arr     = np.array([e["ts_ns"]  for e in events])
sc_arr     = [e["syscall"] for e in events]
proc_arr   = [e["proc"]    for e in events]
boundaries = np.arange(t_normal_start, t_attack_end + window_ns, window_ns)

rows = []
for i in range(len(boundaries) - 1):
    t_w_start = boundaries[i]
    t_w_end   = boundaries[i + 1]
    lo = np.searchsorted(ts_arr, t_w_start, side="left")
    hi = np.searchsorted(ts_arr, t_w_end,   side="left")

    vec    = np.zeros(n_feat, dtype=np.float32)
    w_sc   = sc_arr[lo:hi]
    w_proc = proc_arr[lo:hi]
    n_ev   = len(w_sc)

    for sc in w_sc:
        if sc in sc_idx: vec[sc_idx[sc]] += 1
    for j in range(len(w_sc) - 1):
        bg = (w_sc[j], w_sc[j+1])
        if bg in bg_idx: vec[n_sc + bg_idx[bg]] += 1
    for j in range(len(w_sc) - 2):
        tg = (w_sc[j], w_sc[j+1], w_sc[j+2])
        if tg in tg_idx: vec[n_sc + n_bg + tg_idx[tg]] += 1
    for p in w_proc:
        if p in proc_idx: vec[n_sc + n_bg + n_tg + proc_idx[p]] += 1

    if n_ev > 0:
        vec /= n_ev

    label = 1 if t_w_start >= t_attack_start else 0
    rows.append({"window_start_ns": int(t_w_start), "total_events": n_ev, "label": label,
                 **{feature_names[j]: float(vec[j]) for j in range(n_feat)}})

df = pd.DataFrame(rows)
normal_n = (df["label"] == 0).sum()
attack_n = (df["label"] == 1).sum()
print(f"   총 윈도우: {len(df)}개 (정상: {normal_n}, 공격: {attack_n})")

# 5. 저장 (특성만 있는 CSV + 라벨 포함 전체 CSV + NPY)
print("[5] 저장 중...")
feat_only = df[feature_names]
feat_only.to_csv(f"{OUTPUT_DIR}/features_scenario3.csv", index=False)

df.to_csv(f"{OUTPUT_DIR}/scenario3_features_labeled.csv", index=False)

np.save(f"{OUTPUT_DIR}/features_scenario3.npy", feat_only.values.astype(np.float32))

print(f"\n완료!")
print(f"   features_scenario3.csv     — 특성만 {feat_only.shape}")
print(f"   scenario3_features_labeled.csv — 메타+특성+라벨 {df.shape}")
print(f"   features_scenario3.npy     — shape {feat_only.values.shape}")
