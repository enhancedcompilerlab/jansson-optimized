/* bench_parse.c —— jansson 解析吞吐基准。
 * 读入一个 JSON 文件，在进程内重复 json_loads N 次（避免进程启动开销），
 * 报告 parses/s 与 MB/s。用法: bench_parse <input.json> <iters>
 */
#include <jansson.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s <json> <iters>\n", argv[0]); return 2; }
    int iters = atoi(argv[2]);
    FILE *f = fopen(argv[1], "rb");
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    char *buf = malloc((size_t)n + 1);
    size_t rd = fread(buf, 1, (size_t)n, f);
    buf[rd] = '\0'; fclose(f);
    if (rd == 0) { fprintf(stderr, "empty input\n"); return 2; }

    /* warmup + sanity */
    json_error_t err;
    json_t *r = json_loads(buf, 0, &err);
    if (!r) { fprintf(stderr, "input invalid: %s\n", err.text); return 2; }
    json_decref(r);

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < iters; i++) {
        r = json_loads(buf, 0, &err);
        json_decref(r);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double sec = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    printf("parsed %d x in %.3f s => %.0f parses/s | %.1f MB/s (input %.2f MB)\n",
           iters, sec, iters / sec, (iters * (double)rd / sec) / 1e6, rd / 1e6);
    free(buf);
    return 0;
}
