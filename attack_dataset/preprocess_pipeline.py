#!/usr/bin/env python3
"""
Syscall CSV preprocessing pipeline for Marine attack dataset.
Converts raw sysdig CSV (ts_ns, syscall, proc_name, tid, evt_cpu) into
time-windowed feature vectors with unigram, bigram, trigram, and process features.

Usage:
    python preprocess_pipeline.py <input_csv> [--output-dir <dir>] [--window-sec 5]
"""

import argparse
import csv
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

WINDOW_SEC = 5
NS_PER_SEC = 1_000_000_000

SYSCALL_FEATURES = [
    "mmap", "clock_gettime", "close", "read", "mprotect", "switch", "open",
    "fstat", "access", "brk", "rt_sigaction", "futex", "times", "stat",
    "lstat", "munmap", "dup", "arch_prctl", "execve", "gettimeofday",
    "write", "procexit", "geteuid", "getppid", "exit_group", "getpid",
    "epoll_ctl", "epoll_wait", "rt_sigprocmask", "clone", "setsid", "ioctl",
    "wait4", "uname", "statfs", "signaldeliver", "chdir", "sigreturn",
    "recvfrom", "getpeername", "getsockname", "socket", "connect",
    "setsockopt", "sendto", "sched_yield", "select", "pread", "io_getevents",
    "getcwd", "lseek", "gettid", "set_robust_list", "fcntl", "pwrite",
    "getdents", "container", "openat", "sigaltstack", "getrlimit", "fsync",
    "unlink", "set_tid_address", "sched_getaffinity", "setrlimit", "madvise",
    "exit",
]

BIGRAM_FEATURES = [
    "clock_gettime_clock_gettime", "mmap_mmap", "fstat_mmap", "times_times",
    "access_open", "mmap_close", "mprotect_mprotect", "read_read",
    "open_fstat", "clock_gettime_futex", "rt_sigaction_rt_sigaction",
    "lstat_lstat", "futex_switch", "brk_brk", "mmap_mprotect",
    "close_access", "mmap_arch_prctl", "mprotect_munmap", "mprotect_mmap",
    "read_fstat", "mmap_access", "open_read", "access_mmap", "close_mmap",
    "brk_access", "arch_prctl_mprotect", "execve_brk",
    "switch_clock_gettime", "futex_clock_gettime", "close_close",
    "rt_sigaction_geteuid", "getpid_rt_sigaction", "close_munmap",
    "stat_stat", "getppid_stat", "dup_dup", "brk_getppid", "geteuid_brk",
    "munmap_getpid", "gettimeofday_gettimeofday", "exit_group_procexit",
    "switch_read", "read_switch", "rt_sigaction_read", "close_open",
    "mmap_read", "read_close", "ioctl_rt_sigaction", "uname_statfs",
    "fstat_close", "close_exit_group", "close_rt_sigprocmask",
    "statfs_stat", "rt_sigprocmask_execve", "dup_setsid", "stat_uname",
    "read_clone", "signaldeliver_sigreturn", "lstat_stat", "munmap_close",
    "stat_ioctl", "stat_rt_sigaction", "dup_close", "rt_sigaction_execve",
    "mmap_write", "stat_fstat", "brk_open", "munmap_lstat",
    "sigreturn_write", "procexit_signaldeliver", "chdir_dup",
    "close_execve", "munmap_brk", "setsid_close", "wait4_switch",
    "write_switch", "write_read", "switch_open", "switch_futex", "open_dup",
    "clone_wait4", "read_chdir", "switch_exit_group", "epoll_wait_switch",
    "switch_close", "clock_gettime_socket", "getsockname_getpeername",
    "epoll_ctl_close", "setsockopt_connect", "connect_epoll_ctl",
    "socket_setsockopt", "futex_futex", "getpeername_clock_gettime",
    "procexit_clock_gettime", "epoll_ctl_getsockname", "recvfrom_switch",
    "clock_gettime_write", "read_futex", "gettimeofday_sendto",
    "gettimeofday_recvfrom", "clock_gettime_gettimeofday",
    "epoll_wait_epoll_wait", "switch_recvfrom", "switch_epoll_wait",
    "clock_gettime_read", "recvfrom_clock_gettime", "switch_switch",
    "clock_gettime_epoll_ctl", "switch_procexit", "exit_group_switch",
    "close_clock_gettime", "futex_read", "clock_gettime_epoll_wait",
    "read_clock_gettime", "clock_gettime_sched_yield", "switch_brk",
    "sched_yield_clock_gettime", "write_close", "sendto_gettimeofday",
    "select_switch", "write_clock_gettime", "execve_switch", "close_futex",
    "switch_gettimeofday", "clock_gettime_stat", "read_epoll_ctl",
    "sendto_switch", "read_exit_group", "procexit_read", "switch_select",
    "epoll_ctl_switch", "switch_chdir", "clock_gettime_switch",
    "stat_clock_gettime", "switch_getsockname", "switch_mprotect",
    "switch_dup", "procexit_select", "futex_epoll_wait", "procexit_futex",
    "epoll_wait_clock_gettime", "stat_futex", "munmap_switch",
    "close_switch", "getpeername_epoll_ctl", "open_switch",
    "arch_prctl_switch", "switch_mmap", "procexit_switch", "mmap_switch",
]

TRIGRAM_FEATURES = [
    "times_times_times", "clock_gettime_clock_gettime_clock_gettime",
    "open_fstat_mmap", "read_read_read", "close_access_open",
    "mmap_close_access", "fstat_mmap_close", "fstat_mmap_mprotect",
    "mmap_mprotect_mmap", "read_fstat_mmap", "mmap_mmap_arch_prctl",
    "access_open_read", "mprotect_mprotect_munmap", "mmap_mmap_mmap",
    "lstat_lstat_lstat", "open_read_fstat", "mmap_access_open",
    "access_open_fstat", "access_mmap_access", "mprotect_mmap_mmap",
    "mmap_mmap_close", "close_mmap_mmap", "mmap_close_mmap",
    "brk_access_mmap", "mprotect_mprotect_mprotect",
    "mmap_arch_prctl_mprotect", "arch_prctl_mprotect_mprotect",
    "execve_brk_access", "clock_gettime_futex_switch",
    "rt_sigaction_rt_sigaction_rt_sigaction",
    "getpid_rt_sigaction_geteuid", "brk_brk_getppid",
    "getppid_stat_stat", "brk_getppid_stat",
    "rt_sigaction_geteuid_brk", "geteuid_brk_brk",
    "munmap_getpid_rt_sigaction", "mprotect_munmap_getpid",
    "clock_gettime_clock_gettime_futex",
    "futex_clock_gettime_clock_gettime", "futex_switch_clock_gettime",
    "switch_clock_gettime_futex", "clock_gettime_futex_clock_gettime",
    "gettimeofday_gettimeofday_gettimeofday",
    "rt_sigaction_rt_sigaction_read", "close_close_close",
    "ioctl_rt_sigaction_rt_sigaction", "close_close_rt_sigprocmask",
    "uname_statfs_stat", "fstat_mmap_read", "read_close_munmap",
    "close_rt_sigprocmask_execve", "rt_sigaction_read_clone",
    "fstat_close_open", "stat_uname_statfs", "close_munmap_close",
    "dup_dup_setsid", "stat_ioctl_rt_sigaction",
    "munmap_close_exit_group", "stat_rt_sigaction_rt_sigaction",
    "lstat_lstat_stat", "rt_sigaction_rt_sigaction_execve",
    "stat_stat_ioctl", "lstat_stat_uname", "dup_dup_dup",
    "open_fstat_close", "stat_stat_rt_sigaction", "fstat_mmap_write",
    "stat_fstat_mmap", "statfs_stat_fstat", "brk_brk_open",
    "close_munmap_lstat", "munmap_lstat_lstat", "brk_open_fstat",
    "mmap_read_read", "signaldeliver_sigreturn_write",
    "read_read_close", "procexit_signaldeliver_sigreturn",
    "close_open_fstat", "chdir_dup_dup", "dup_close_execve",
    "close_exit_group_procexit", "munmap_brk_brk",
    "mprotect_munmap_brk", "setsid_close_close",
    "exit_group_procexit_signaldeliver", "dup_setsid_close",
    "rt_sigprocmask_execve_brk", "open_dup_close", "switch_open_dup",
    "close_execve_brk", "switch_read_read", "read_clone_wait4",
    "wait4_switch_open", "rt_sigaction_execve_brk", "clone_wait4_switch",
    "read_chdir_dup", "read_read_chdir", "write_read_switch",
    "read_switch_exit_group",
]

PROC_FEATURES = [
    "sh", "df", "user", "erl_child_setup", "mysqld", "mongod",
    "container:011fdbdbf777", "container:95cf5d7c594f",
    "container:f8cd5974589d", "container:7aeb4e77cfbf",
]


def load_raw_csv(filepath):
    """Load raw sysdig CSV and return list of (ts_ns, syscall, proc_name, tid, evt_cpu)."""
    rows = []
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) < 5:
                continue
            try:
                ts = int(row[0])
            except ValueError:
                continue
            rows.append((ts, row[1], row[2], row[3], row[4]))
    return rows


def extract_features(rows, window_sec=WINDOW_SEC):
    """Extract time-windowed feature vectors from raw syscall rows."""
    if not rows:
        return np.array([]), []

    sc_set = set(SYSCALL_FEATURES)
    bg_set = set(BIGRAM_FEATURES)
    tg_set = set(TRIGRAM_FEATURES)
    proc_set = set(PROC_FEATURES)

    first_ts = rows[0][0]
    last_ts = rows[-1][0]
    window_ns = window_sec * NS_PER_SEC
    n_windows = max(1, int((last_ts - first_ts) / window_ns) + 1)

    all_features = []
    header = (
        [f"sc_{s}" for s in SYSCALL_FEATURES]
        + [f"bg_{b}" for b in BIGRAM_FEATURES]
        + [f"tg_{t}" for t in TRIGRAM_FEATURES]
        + [f"proc_{p}" for p in PROC_FEATURES]
    )

    windows = [[] for _ in range(n_windows)]
    for row in rows:
        ts = row[0]
        win_idx = min(int((ts - first_ts) / window_ns), n_windows - 1)
        windows[win_idx].append(row)

    for win_rows in windows:
        sc_counts = Counter()
        bg_counts = Counter()
        tg_counts = Counter()
        proc_names = set()

        syscalls = []
        for _, syscall, proc_name, _, _ in win_rows:
            sc_counts[syscall] += 1
            syscalls.append(syscall)
            proc_names.add(proc_name)

        total_sc = sum(sc_counts.values()) if sc_counts else 1

        for i in range(len(syscalls) - 1):
            bg_key = f"{syscalls[i]}_{syscalls[i+1]}"
            bg_counts[bg_key] += 1

        total_bg = sum(bg_counts.values()) if bg_counts else 1

        for i in range(len(syscalls) - 2):
            tg_key = f"{syscalls[i]}_{syscalls[i+1]}_{syscalls[i+2]}"
            tg_counts[tg_key] += 1

        total_tg = sum(tg_counts.values()) if tg_counts else 1

        feature_vec = []
        for s in SYSCALL_FEATURES:
            feature_vec.append(sc_counts.get(s, 0) / total_sc)
        for b in BIGRAM_FEATURES:
            feature_vec.append(bg_counts.get(b, 0) / total_bg)
        for t in TRIGRAM_FEATURES:
            feature_vec.append(tg_counts.get(t, 0) / total_tg)
        for p in PROC_FEATURES:
            feature_vec.append(1.0 if p in proc_names else 0.0)

        all_features.append(feature_vec)

    return np.array(all_features, dtype=np.float32), header


def save_outputs(features, header, output_dir, basename):
    """Save feature matrix as both CSV and NPY."""
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, f"features_{basename}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in features:
            writer.writerow([f"{v:.10g}" for v in row])

    npy_path = os.path.join(output_dir, f"features_{basename}.npy")
    np.save(npy_path, features)

    return csv_path, npy_path


def main():
    parser = argparse.ArgumentParser(description="Preprocess raw sysdig CSV into feature vectors")
    parser.add_argument("input_csv", help="Path to raw sysdig CSV file")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--window-sec", type=int, default=WINDOW_SEC, help="Window size in seconds (default: 5)")
    parser.add_argument("--name", default=None, help="Output basename (default: derived from input filename)")
    args = parser.parse_args()

    input_path = args.input_csv
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    basename = args.name or Path(input_path).stem.replace("raw_", "")

    print(f"Loading {input_path}...")
    rows = load_raw_csv(input_path)
    print(f"  Loaded {len(rows)} rows")

    print(f"Extracting features (window={args.window_sec}s)...")
    features, header = extract_features(rows, window_sec=args.window_sec)
    print(f"  Generated {features.shape[0]} windows x {features.shape[1]} features")

    csv_path, npy_path = save_outputs(features, header, args.output_dir, basename)
    print(f"  Saved: {csv_path}")
    print(f"  Saved: {npy_path}")


if __name__ == "__main__":
    main()
