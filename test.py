"""
Bộ test "chuẩn vàng" (golden) cho 3 module, dùng chung với vdp_contract.py.

Ý tưởng chống xung đột: mỗi module được test ĐỘC LẬP bằng dữ liệu chuẩn,
nên 3 người không phải chờ nhau.
  - test A (Key Point): chỉ dùng source + api_list.
  - test B (Slicing):   nhận Key Point CHUẨN làm đầu vào (không phụ thuộc người A).
  - test C (Gadget):    nhận các Slice CHUẨN làm đầu vào (không phụ thuộc người B).
  - test ghép cả 3:     chỉ chạy được khi cả ba đã xong.

Chạy:  python test_golden.py
Mỗi dòng kết quả là PASS (đúng) / FAIL (sai, kèm chi tiết) / TODO (chưa cài đặt).

Ví dụ 1 lấy từ Figure 3 của bài báo (đáp án khớp mô tả trong mục III.C và III.D).
Ví dụ 2 là bài tập helper/main đã luyện, làm theo đúng quy ước Q3 (chỉ data dependency).
Nhóm nên tự thêm 2-3 ví dụ nữa vào CASES (mỗi ví dụ do một người viết, người khác duyệt).
"""
import sys

import vdp_contract as vdp
from vdp_contract import KeyPoint, Slice, Statement

# recv là forward theo bài báo; hướng các hàm khác nhóm tự chốt trong api_list.json.
API_LIST = {"strcpy": "backward", "recv": "forward"}

# ----- Ví dụ 1: Figure 3 của bài báo (22 dòng) -----
FIG3_LINES = [
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
assert len(FIG3_LINES) == 22

# ----- Ví dụ 2: bài tập helper/main (14 dòng) -----
EX2_LINES = [
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
assert len(EX2_LINES) == 14

CASES = [
    {
        "name": "Ví dụ 1 - Figure 3 của bài báo",
        "source": "\n".join(FIG3_LINES),
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
    },
    {
        "name": "Ví dụ 2 - bài tập helper/main (chỉ data dependency)",
        "source": "\n".join(EX2_LINES),
        "key_point": ("strcpy", "helper", 4, ("temp", "input"), "backward"),
        "slices": {
            "temp": [("helper", 2), ("helper", 3), ("helper", 4)],
            "input": [("main", 7), ("main", 8), ("main", 10), ("main", 11),
                      ("helper", 1), ("helper", 4)],
        },
        "gadget": [("main", 7), ("main", 8), ("main", 10), ("main", 11),
                   ("helper", 1), ("helper", 2), ("helper", 3), ("helper", 4)],
    },
]


# ----------------------------- hàm phụ trợ -----------------------------
def _stmt(source, func, line):
    return Statement(func, line, source.splitlines()[line - 1].strip())


def _kp(spec):
    api, func, line, args, direction = spec
    return KeyPoint(api, func, line, tuple(args), direction)


def _slice(case, kp, arg):
    sts = tuple(_stmt(case["source"], f, l) for f, l in case["slices"][arg])
    return Slice(kp, arg, kp.direction, sts)


def _pairs(statements):
    return [(s.func, s.line) for s in statements]


# ------------------------------- các test -------------------------------
def test_key_points(case):
    got = vdp.extract_key_points(case["source"], API_LIST)
    want = _kp(case["key_point"])
    assert len(got) == 1, f"mong đợi 1 Key Point, nhận {len(got)}"
    k = got[0]
    assert (k.api, k.func, k.line, tuple(k.args), k.direction) == \
           (want.api, want.func, want.line, want.args, want.direction), \
           f"mong đợi {want}, nhận {k}"


def test_slices(case):
    kp = _kp(case["key_point"])  # Key Point chuẩn làm đầu vào
    got = vdp.build_slices(case["source"], kp)
    by_arg = {}
    for s in got:
        by_arg.setdefault(s.arg, []).append(_pairs(s.statements))
    for arg, want in case["slices"].items():
        assert arg in by_arg, f"thiếu slice cho đối số '{arg}'"
        assert want in by_arg[arg], \
            f"slice của '{arg}': mong đợi {want}, nhận {by_arg[arg]}"
    extra = set(by_arg) - set(case["slices"])
    assert not extra, f"có slice thừa cho đối số: {extra}"


def test_gadget(case):
    kp = _kp(case["key_point"])
    slices = [_slice(case, kp, a) for a in case["slices"]]  # Slice chuẩn làm đầu vào
    g = vdp.assemble_gadget(kp, slices)
    assert _pairs(g.statements) == case["gadget"], \
        f"mong đợi {case['gadget']}, nhận {_pairs(g.statements)}"


def test_pipeline(case):
    gs = vdp.run_pipeline(case["source"], API_LIST)
    assert len(gs) == 1, f"mong đợi 1 gadget, nhận {len(gs)}"
    assert _pairs(gs[0].statements) == case["gadget"], \
        f"mong đợi {case['gadget']}, nhận {_pairs(gs[0].statements)}"


TESTS = [
    ("A  Key Point   ", test_key_points),
    ("B  Slicing     ", test_slices),
    ("C  Code Gadget ", test_gadget),
    ("   Ghép cả 3   ", test_pipeline),
]


def main():
    n_fail = 0
    for case in CASES:
        print(f"\n== {case['name']} ==")
        for label, fn in TESTS:
            try:
                fn(case)
                print(f"  PASS  {label}")
            except NotImplementedError as e:
                print(f"  TODO  {label} ({e})")
            except AssertionError as e:
                n_fail += 1
                print(f"  FAIL  {label}: {e}")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
