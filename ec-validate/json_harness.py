#!/usr/bin/env python3
"""jansson 差分 runner：对语料中每个 JSON，分别跑 driver_base 与 driver_cand，
比对 (exit code, stdout, stderr)。jansson dump 输出是纯数据（无内存地址），无需归一化。
用法: json_harness.py <driver_base> [driver_cand] [corpus_dir]
若 candidate 未给，默认等于 base（用于自检脚手架）。
"""
import subprocess, sys, os, glob

BASE = sys.argv[1]
CAND = sys.argv[2] if len(sys.argv) > 2 else BASE
CORPUS = sys.argv[3] if len(sys.argv) > 3 else "corpus"
TIMEOUT = 30


def run(driver, f):
    try:
        r = subprocess.run([driver, f], capture_output=True, timeout=TIMEOUT)
        return (r.returncode, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", b"", b"")


files = sorted(glob.glob(os.path.join(CORPUS, "*.json")))
mism = []
for f in files:
    a = run(BASE, f)
    b = run(CAND, f)
    if a != b:
        mism.append((f, a, b))

print(f"json files={len(files)}  mismatches={len(mism)}")
for f, a, b in mism[:25]:
    print("=" * 60)
    print("MISMATCH:", f)
    print("  base:", a[0], repr(a[1][:200]), repr(a[2][:100]))
    print("  cand:", b[0], repr(b[1][:200]), repr(b[2][:100]))
sys.exit(1 if mism else 0)
