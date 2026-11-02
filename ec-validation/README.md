# ec-validation — jansson 优化验证（差分测试 + Fuzz）

对"优化版（本仓库 `src/load.c`）vs 未改动基线"做**行为等价性**验证。

## 方法：差分测试 + Fuzz

- **差分测试**：对同一输入，分别跑 `driver_base`（未改动基线）与 `driver_cand`（优化版），比对 `(exit code, stdout, stderr)`。以基线为基准，**连 bug 都要保持一致**——测的是行为等价性，不是行为正确性。
- **Fuzz**：自动生成海量随机 + 定向边界输入（0 长度、深嵌套、非法数字、重复键、surrogate、NUL、控制字符、负零等），专炸边界，为差分提供判据。
- 只适用于**确定性程序**（同输入→同输出）：解析器/解释器/压缩库等。jansson 满足。

## 组成

| 文件 | 说明 |
|---|---|
| `json_harness.py` | 差分 runner：逐输入比对 base/cand 的 exit/stdout/stderr |
| `gen_json.py` | 语料生成器：300 随机合法 + 26 定向非法/边界（seed 固定 20261102） |
| `corpus/` | 已生成的 **326 个**输入（提交入库，保证可复现） |
| `driver.c` | 被测程序：读 JSON → `json_loads(JSON_REJECT_DUPLICATES)` → 规范化 dump；错误打印 ERR line/col/pos |
| `build.sh` | 从两个源码树编译 `driver_base` 与 `driver_cand` |

> jansson 的 dump 输出是纯数据（无内存地址），无需归一化；这是选它做第一个靶场的优势之一。

## 运行

```bash
# 1) 构建两个 driver：baseline 需未改动的官方源码树（如 git clone https://github.com/akheron/jansson）
./build.sh /path/to/akheron/jansson       # optimized 默认用本仓库 ../src

# 2) 差分门禁：必须 0 不一致
python3 json_harness.py out/driver_base out/driver_cand corpus
```

## 结果

**326 个输入，0 不一致** —— 优化版与基线行为完全等价。
