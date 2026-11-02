#!/bin/bash
# build.sh —— 从两个 jansson 源码树编译被测 driver：
#   driver_base = 未改动的官方 jansson 源码树
#   driver_cand = 优化版源码树（默认本仓库 src/，已含字符串批量 run 优化）
# 用法: ./build.sh <baseline_srcdir> [optimized_srcdir]
# 前提: 两个源码树都需已生成 src/jansson_config.h（官方由 autotools/cmake configure 生成，
#        或用测试中手写的等价配置），并已含 src/*.c。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE_SRC="$1"
OPT_SRC="${2:-$HERE/../src}"
CFLAGS="-std=gnu99 -O3 -include stdint.h"
mkdir -p "$HERE/out"

build_driver() {
  local srcdir="$1" name="$2"
  local tmp
  tmp="$(mktemp -d)"
  ( cd "$srcdir" && gcc $CFLAGS -I src -c src/*.c )
  ar rcs "$tmp/lib.a" "$srcdir"/*.o
  rm -f "$srcdir"/*.o
  gcc -O2 -I "$srcdir/src" "$HERE/driver.c" "$tmp/lib.a" -o "$HERE/out/driver_$name" -lm
  rm -rf "$tmp"
}

build_driver "$BASE_SRC" base
build_driver "$OPT_SRC" cand
echo "built $HERE/out/driver_base (baseline) and $HERE/out/driver_cand (optimized)"
