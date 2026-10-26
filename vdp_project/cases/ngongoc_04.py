
"""
Ví dụ 5 - Kiểm thử chung cho thành viên A, B và C.

Mục tiêu:
- Thành viên C: Nhận diện Key Point từ danh sách API.
- Thành viên B: Xây dựng backward slice cho từng đối số của Key Point.
- Thành viên C: Hợp nhất các slice thành Code Gadget.

Kịch bản:
- memcpy(dst, src, sizeof(src)) là Key Point.
- dst là vùng nhớ đích.
- src là vùng nhớ nguồn.
- unused và printf("done") không liên quan đến Key Point.
- Hướng phân tích là backward.

Lưu ý:
- Dòng số trong các slice được tính từ 1.
- Đáp án B dưới đây khớp với kết quả slicer.py hiện tại,
  trong đó dòng khai báo hàm main được đưa vào slice của src.
"""

LINES = [
    "int main(int argc, char **argv) {",  # 1
    "  char dst[32];",                    # 2
    "  char src[32];",                    # 3
    "  int unused = 10;",                 # 4
    "  src[0] = argv[1][0];",             # 5
    "  memcpy(dst, src, sizeof(src));",   # 6
    '  printf("done");',                  # 7
    "  return 0;",                        # 8
    "}",                                  # 9
]

CASE = {
    "name": "Ví dụ 5 - memcpy backward",
    "source": "\n".join(LINES),

    "key_point": (
        "memcpy",              # API cần nhận diện
        "main",                # Hàm chứa API
        6,                     # Dòng chứa Key Point
        ("dst", "src", "sizeof(src)"),
        "backward",            # Truy vết ngược
    ),

  
    "slices": {
        # Slice của dst:
        # Dòng 2 khai báo dst; dòng 6 sử dụng dst.
        "dst": [
            ("main", 2),
            ("main", 6),
        ],

        "src": [
            ("main", 1),
            ("main", 3),
            ("main", 5),
            ("main", 6),
        ],

        # Slice của sizeof(src):
        # Dòng 3 khai báo src; dòng 6 dùng sizeof(src).
        "sizeof(src)": [
              ("main", 1),
              ("main", 3),
              ("main", 5),
              ("main", 6),
              ],
    },

 
    "gadget": [
        ("main", 1),
        ("main", 2),
        ("main", 3),
        ("main", 5),
        ("main", 6),
    ],
}
