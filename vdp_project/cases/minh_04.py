"""Ví dụ 4 (thành viên A - Minh): hàm trả về con trỏ + tên API nằm trong comment và chuỗi."""

LINES = [
    "char *",                                    # 1
    "copy_name(char *src) {",                    # 2
    "  char buf[16];",                           # 3
    "  /* strcpy(buf, src) would be unsafe */",  # 4
    '  printf("strcpy(buf, src)");',             # 5
    "  strcpy(buf, src);",                       # 6
    "  return buf;",                             # 7
    "}",                                         # 8
    "",                                          # 9
    "int main(int argc, char **argv) {",         # 10
    "  char *name;",                             # 11
    "  name = argv[1];",                         # 12
    "  copy_name(name);",                        # 13
    "  return 0;",                               # 14
    "}",                                         # 15
]
assert len(LINES) == 15

CASE = {
    "name": "Ví dụ 4 - hàm trả về con trỏ, API trong comment/chuỗi (thành viên A)",
    "source": "\n".join(LINES),
    "key_point": ("strcpy", "copy_name", 6, ("buf", "src"), "backward"),
    "slices": {
        "buf": [("copy_name", 3), ("copy_name", 6)],
        "src": [("main", 10), ("main", 11), ("main", 12), ("main", 13),
                ("copy_name", 2), ("copy_name", 6)],
    },
    "gadget": [("main", 10), ("main", 11), ("main", 12), ("main", 13),
               ("copy_name", 2), ("copy_name", 3), ("copy_name", 6)],
}