#!/usr/bin/env python3
"""生成 JSON 差分测试语料：随机合法 JSON + 非法/边界用例。
确定性：固定 seed。用法: gen_json.py [seed] [count] [outdir]
"""
import random, os, sys

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20261102
N = int(sys.argv[2]) if len(sys.argv) > 2 else 300
OUT = sys.argv[3] if len(sys.argv) > 3 else "corpus"
random.seed(SEED)
os.makedirs(OUT, exist_ok=True)

KEYS = ["a", "b", "key", "k2", "name", "value", "x", "yy", "α", "中", "a b", "1"]
STRS = ["", "hello", "esc\"q", "back\\slash", "newline\n", "tab\t", "unicode\u00e9",
        "中文", "emoji\U0001F600", "   pad  ", "x" * 40, "quote\"", "\b\f\r"]


def numlit():
    r = random.random()
    if r < 0.5:
        return str(random.randint(-10**9, 10**9))
    f = random.uniform(-1e6, 1e6)
    if r < 0.65:
        return repr(round(f, random.randint(0, 6)))
    if r < 0.85:
        return f"{f:.8e}" if random.random() < 0.5 else f"{f:g}"
    # exponent forms
    return f"{random.randint(1,99)}e{random.randint(-6,6)}"


def strlit():
    s = random.choice(STRS)
    if random.random() < 0.3:
        s = "".join(random.choice("abcXYZ019\\\"\\n\\t\u00e9中") for _ in range(random.randint(0, 15)))
    return json_escape(s)


def json_escape(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') \
                 .replace('\t', '\\t').replace('\r', '\\r').replace('\b', '\\b') \
                 .replace('\f', '\\f') + '"'


def value(d):
    if d <= 0:
        return random.choice(["null", "true", "false", "1", "-7", "0", "[]", "{}", '"s"'])
    r = random.random()
    if r < 0.13:
        return "null"
    if r < 0.21:
        return "true"
    if r < 0.27:
        return "false"
    if r < 0.45:
        return numlit()
    if r < 0.60:
        return strlit()
    if r < 0.82:
        return array(d - 1)
    return obj(d - 1)


def array(d):
    n = random.randint(0, 6)
    return "[" + ",".join(value(d) for _ in range(n)) + "]"


def obj(d):
    n = random.randint(0, 5)
    pairs = []
    for _ in range(n):
        pairs.append(f"{strlit()}: {value(d)}")
    return "{" + ",".join(pairs) + "}"


def valid_json():
    return value(random.randint(1, 6))


# 定向非法/边界用例（可复现，专炸解析器边界）
TARGETED = {
    "edge_empty.json": "",
    "edge_ws_only.json": "   \n\t  ",
    "edge_truncated_obj.json": '{"a": 1,',
    "edge_truncated_arr.json": '[1, 2,',
    "edge_unclosed_str.json": '{"a": "abc}',
    "edge_bad_escape.json": '{"a": "\\x41"}',
    "edge_bad_number_1.json": '[1.2.3]',
    "edge_bad_number_2.json": '[01]',
    "edge_bad_number_3.json": '[1e]',
    "edge_bad_number_4.json": '[1e+]',
    "edge_bad_number_5.json": '[NaN]',
    "edge_bad_number_6.json": '[+1]',
    "edge_dup_key.json": '{"a": 1, "a": 2}',
    "edge_control_char_str.json": '{"a": "x\x01y"}',
    "edge_trailing_garbage.json": '{"a": 1} extra',
    "edge_missing_colon.json": '{"a" 1}',
    "edge_missing_comma.json": '[1 2]',
    "edge_lone_brace.json": '}',
    "edge_deep_nest.json": '[' * 5000 + ']' * 5000,
    "edge_big_int.json": '[1234567890123456789012345678901234567890]',
    "edge_neg_zero.json": '[-0.0, 0.0, -0, 0]',
    "edge_exp_bounds.json": '[1e308, 1e-308, -1e308]',
    "edge_unicode_surrogate.json": '["\\ud83d\\ude00", "\\ud800"]',
    "edge_null_in_str.json": '{"a": "x\x00y"}',
    "edge_only_number.json": '42.5',
    "edge_mixed_types.json": '[null, true, false, 0, 1.5, "s", [], {}, [[[1]]]]',
}

written = 0
for i in range(N):
    p = valid_json()
    fn = os.path.join(OUT, f"json_{i:04d}.json")
    with open(fn, "w") as f:
        f.write(p)
    written += 1
for name, body in TARGETED.items():
    with open(os.path.join(OUT, name), "w") as f:
        f.write(body)
    written += 1
print(f"wrote {written} json files to {OUT} (seed={SEED})")
