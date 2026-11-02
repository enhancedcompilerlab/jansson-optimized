# EC-OPT-DOC — Enhanced Compiler 优化文档

本目录记录对 **jansson 2.15.1** 的 "AI 代码生成即 enhanced compiler" 源码级优化：改了什么、为什么是编译器式优化、如何验证、性能与负结果。后续对其它项目（如 Lua VM）做优化时，也在此目录各建子文档归档。

## 研究 idea

把 AI 代码生成当作 **enhanced compiler**：AI 改写源码，但只做传统编译优化范畴内的事（消除逐字节冗余、批量访存、loop 级 partial specialization 等），**不换更高层算法**；结合程序语义上下文，做到保守编译器（GCC/Clang）因函数指针抽象、别名、可观测状态而不敢做的优化；正确性靠差分测试保证。

## 文档索引

| 文件 | 内容 |
|---|---|
| [OPTIMIZATION.md](OPTIMIZATION.md) | 已落地优化：字符串 token 扫描的批量 plain-run（唯一改动 `src/load.c`） |
| [NEGATIVE-RESULT.md](NEGATIVE-RESULT.md) | 探索未纳入：数字/关键字批量 run（行为等价但实测无收益） |

## 配套目录

| 目录 | 内容 |
|---|---|
| [`../ec-validate/`](../ec-validate/) | 验证：差分测试 + Fuzz（harness、语料生成器、326 个 corpus、driver） |
| [`../ec-benchmark/`](../ec-benchmark/) | 基准：进程内解析吞吐（bench 程序 + 各类负载 + 结果） |
