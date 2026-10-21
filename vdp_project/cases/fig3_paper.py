"""Ví dụ 1: Figure 3 của bài báo (22 dòng). Đáp án khớp mô tả ở mục III.C và III.D."""

LINES = [
    "void",                                      # 1
    "test(char *str)",                           # 2
    "{",                                         # 3
    "  int MAXSIZE=40;",                         # 4
    "  char buf[MAXSIZE];",                      # 5
    "",                                          # 6
    "  if(!buf)",                                # 7
    "    return;",                               # 8
    "  strcpy(buf, str); /*string copy*/",       # 9
    "}",                                         # 10
    "",                                          # 11
    "int",                                       # 12
    "main(int argc, char **argv)",               # 13
    "{",                                         # 14
    "  char *userstr;",                          # 15
    "",                                          # 16
    "  if(argc > 1) {",                          # 17
    "    userstr = argv[1];",                    # 18
    "    test(userstr);",                        # 19
    "  }",                                       # 20
    "  return 0;",                               # 21
    "}",                                         # 22
]
assert len(LINES) == 22

CASE = {
    "name": "Ví dụ 1 - Figure 3 của bài báo",
    "source": "\n".join(LINES),
    # (api, hàm chứa, dòng, các đối số, hướng)
    "key_point": ("strcpy", "test", 9, ("buf", "str"), "backward"),
    # đối số -> chuỗi (hàm, dòng) theo thứ tự chain
    "slices": {
        "buf": [("test", 4), ("test", 5), ("test", 9)],
        "str": [("main", 13), ("main", 15), ("main", 18), ("main", 19),
                ("test", 2), ("test", 9)],
    },
    "gadget": [("main", 13), ("main", 15), ("main", 18), ("main", 19),
               ("test", 2), ("test", 4), ("test", 5), ("test", 9)],
}
