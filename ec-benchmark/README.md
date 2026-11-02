# ec-benchmark — jansson 优化吞吐基准

对优化版 jansson 做进程内解析吞吐测量，用于量化优化收益。

## 方法

`bench_parse.c` 读入一个 JSON 文件，在**进程内重复 `json_loads` N 次**（避免进程启动开销），报告 `parses/s` 与 `MB/s`。只测确定性的解析路径；绝对 MB/s 受机器负载影响，**相对增益**是稳定判据。

## 组成

| 文件 | 说明 |
|---|---|
| `bench_parse.c` | 吞吐基准程序（读入负载文件，进程内重复解析） |
| `workloads/` | 各类负载：字符串密集、混合真实、数字密集、关键字密集 |

## 运行

```bash
# 编译（OPT_SRC 为优化版源码树，需已生成 src/jansson_config.h）
gcc -O2 -I <OPT_SRC>/src ec-benchmark/bench_parse.c <OPT_SRC的lib>.a -o bench -lm

# 测吞吐（iters 取足够大以稳定计时）
./bench workloads/bench_str.json 300
./bench workloads/bench_big.json 150
```

## 负载与结果（2 核云 VM；baseline = 未改动 jansson，candidate = 本仓库优化版）

| 负载 | 说明 | 大小 | baseline | candidate | 提升 |
|---|---|---|---|---|---|
| `bench_str.json` | 字符串密集（长字符串为主） | 0.86MB | ≈112 MB/s | ≈213 MB/s | **+90%** |
| `bench_big.json` | 混合真实负载（对象/字符串/数字/数组） | 0.91MB | ≈37 MB/s | ≈39 MB/s | **+5%** |
| `bench_num.json` | 数字密集（平铺浮点数数组） | 1.77MB | ≈35 MB/s | ≈35 MB/s | ~0% |
| `bench_kw.json` | 关键字密集（true/false/null 数组） | 2.13MB | ≈64 MB/s | ≈65 MB/s | +~1% |

字符串负载收益最大，印证优化命中字符串扫描；数字/关键字 ~0 为负结果，分析见 [`../ec-docs/NEGATIVE-RESULT.md`](../ec-docs/NEGATIVE-RESULT.md)。
