"""Ví dụ 2: bài tập helper/main, làm theo quy ước Q3 (chỉ data dependency)."""

LINES = [
    "void helper(char *input) {",                # 1
    "  int limit = 20;",                         # 2
    "  char temp[limit];",                       # 3
    "  strcpy(temp, input);",                    # 4
    "}",                                         # 5
    "",                                          # 6
    "int main(int argc, char **argv) {",         # 7
    "  char *data;",                             # 8
    "  if (argc > 1) {",                         # 9
    "    data = argv[1];",                       # 10
    "    helper(data);",                         # 11
    "  }",                                       # 12
    "  return 0;",                               # 13
    "}",                                         # 14
]
assert len(LINES) == 14

CASE = {
    "name": "Ví dụ 2 - bài tập helper/main (chỉ data dependency)",
    "source": "\n".join(LINES),
    "key_point": ("strcpy", "helper", 4, ("temp", "input"), "backward"),
    "slices": {
        "temp": [("helper", 2), ("helper", 3), ("helper", 4)],
        "input": [("main", 7), ("main", 8), ("main", 10), ("main", 11),
                  ("helper", 1), ("helper", 4)],
    },
    "gadget": [("main", 7), ("main", 8), ("main", 10), ("main", 11),
               ("helper", 1), ("helper", 2), ("helper", 3), ("helper", 4)],
}
