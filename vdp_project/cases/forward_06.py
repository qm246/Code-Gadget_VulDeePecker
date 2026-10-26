
"""Test forward slicing qua nhiều hàm:
recv() -> receive_data() -> main() -> print_data().
"""

LINES = [
    "void",                                      # 1
    "receive_data(char *buf) {",                 # 2
    "  int sock = 1;",                           # 3
    "  recv(sock, buf, 63, 0);",                 # 4 - Key Point
    "}",                                         # 5
    "",                                          # 6
    "void",                                      # 7
    "print_data(char *data) {",                  # 8
    '  printf("%s", data);',                     # 9
    "}",                                         # 10
    "",                                          # 11
    "int main() {",                              # 12
    "  char buf[64];",                           # 13
    "  receive_data(buf);",                      # 14
    "  print_data(buf);",                        # 15
    "  return 0;",                               # 16
    "}",                                         # 17
]
assert len(LINES) == 17

CASE = {
    "name": "Forward slicing - truyền dữ liệu qua nhiều hàm",
    "source": "\n".join(LINES),

    # (API, hàm chứa Key Point, dòng, đối số, hướng)
    "key_point": (
        "recv",
        "receive_data",
        4,
        ("sock", "buf", "63", "0"),
        "forward",
    ),

    # Mỗi danh sách gồm (tên hàm, số dòng).
    "slices": {
        # sock là tham số điều khiển việc gọi recv,
        # nhưng không được sử dụng tiếp trong ví dụ.
        "sock": [
            ("receive_data", 4),
        ],

        # Dữ liệu được nhận vào buf, sau đó truyền qua main
        # và tiếp tục được sử dụng trong print_data.
        "buf": [
            ("receive_data", 4),
            ("main", 14),
            ("main", 15),
            ("print_data", 8),
            ("print_data", 9),
        ],

        # Hai đối số hằng không có luồng dữ liệu tiếp nối.
        "63": [
            ("receive_data", 4),
        ],
        "0": [
            ("receive_data", 4),
        ],
    },

    # Hợp các câu lệnh thuộc các slice, không lặp câu lệnh.
    "gadget": [
        ("receive_data", 4),
        ("main", 14),
        ("main", 15),
        ("print_data", 8),
        ("print_data", 9),
    ],
}
