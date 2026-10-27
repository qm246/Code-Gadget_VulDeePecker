LINES = [
    "int main() {",                    # 1
    "  char buf[32];",                 # 2
    "  recv(sock, buf, 10, 0);",       # 3 - Key Point
    "  char *copy;",                   # 4
    "  copy = buf;",                   # 5
    "  char *result;",                 # 6
    "  result = copy;",                # 7
    '  printf("%s", result);',         # 8
    "  return 0;",                     # 9
    "}",
]

CASE = {
    "name": "Forward 2 - chuỗi phụ thuộc buf/copy/result",
    "source": "\n".join(LINES),

    "key_point": (
        "recv",
        "main",
        3,
        ("sock", "buf", "10", "0"),
        "forward",
    ),

    "slices": {
        "sock": [
            ("main", 3),
        ],
        "buf": [
            ("main", 3),
            ("main", 5),
            ("main", 7),
            ("main", 8),
        ],
        "10": [
            ("main", 3),
        ],
        "0": [
            ("main", 3),
        ],
    },

    "gadget": [
        ("main", 3),
        ("main", 5),
        ("main", 7),
        ("main", 8),
    ],
}