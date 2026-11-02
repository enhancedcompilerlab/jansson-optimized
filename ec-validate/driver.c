/* driver.c —— jansson 差分/benchmark 的统一驱动。
 * 读入一个 JSON 文件 -> json_loads -> 规范化 dump 输出。
 * 输出确定性：JSON_SORT_KEYS 固定键序，JSON_REJECT_DUPLICATES 让重复键行为明确。
 * 差分即比较 (exit code, stdout)。用法: driver <input.json>
 */
#include <jansson.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    FILE *f = fopen(argv[1], "rb");
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (n < 0) { fclose(f); return 2; }
    char *buf = malloc((size_t)n + 1);
    if (!buf) { fclose(f); return 2; }
    size_t rd = fread(buf, 1, (size_t)n, f);
    buf[rd] = '\0';
    fclose(f);

    json_error_t err;
    json_t *root = json_loads(buf, JSON_REJECT_DUPLICATES, &err);
    free(buf);
    if (!root) {
        printf("ERR line=%d col=%d pos=%d text=%s\n",
               err.line, err.column, err.position, err.text);
        return 1;
    }
    char *d = json_dumps(root, JSON_ENSURE_ASCII | JSON_SORT_KEYS);
    if (!d) { json_decref(root); return 1; }
    printf("%s\n", d);
    free(d);
    json_decref(root);
    return 0;
}
