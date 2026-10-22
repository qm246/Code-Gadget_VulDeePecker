"""Ví dụ 3 (thành viên C - Tài): chuỗi gọi hàm 3 tầng main -> relay -> sink (chỉ data dependency).

Mục đích: kiểm tra assemble_gadget giữ đúng thứ tự main -> relay -> sink khi
slice của đối số thứ nhất (dst) chỉ đi qua relay và sink, còn slice của đối số thứ hai (src)
đi qua cả ba hàm. Đáp án cần được cả nhóm duyệt (đặc biệt phần slicing của B).
"""

LINES = [
    "void sink(char *dst, char *src) {",         # 1
    "  strcpy(dst, src);",                       # 2
    "}",                                         # 3
    "",                                          # 4
    "void relay(char *msg) {",                   # 5
    "  char buf[32];",                           # 6
    "  sink(buf, msg);",                         # 7
    "}",                                         # 8
    "",                                          # 9
    "int main(int argc, char **argv) {",         # 10
    "  char *input;",                            # 11
    "  input = argv[1];",                        # 12
    "  relay(input);",                           # 13
    "  return 0;",                               # 14
    "}",                                         # 15
]
assert len(LINES) == 15

CASE = {
    "name": "Ví dụ 3 - chuỗi 3 hàm main/relay/sink (thành viên C)",
    "source": "\n".join(LINES),
    "key_point": ("strcpy", "sink", 2, ("dst", "src"), "backward"),
    "slices": {
        "dst": [("relay", 6), ("relay", 7), ("sink", 1), ("sink", 2)],
        "src": [("main", 10), ("main", 11), ("main", 12), ("main", 13),
                ("relay", 5), ("relay", 7), ("sink", 1), ("sink", 2)],
    },
    "gadget": [("main", 10), ("main", 11), ("main", 12), ("main", 13),
               ("relay", 5), ("relay", 6), ("relay", 7),
               ("sink", 1), ("sink", 2)],
}
