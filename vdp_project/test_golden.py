"""
Bộ test "chuẩn vàng" (golden) cho 3 module.

Ý tưởng chống xung đột: mỗi module được test ĐỘC LẬP bằng dữ liệu chuẩn,
nên 3 người không phải chờ nhau.
  - test A (Key Point): chỉ dùng source + api_list.
  - test B (Slicing):   nhận Key Point CHUẨN làm đầu vào (không phụ thuộc người A).
  - test C (Gadget):    nhận các Slice CHUẨN làm đầu vào (không phụ thuộc người B).
  - test ghép cả 3:     chỉ chạy được khi cả ba đã xong.

Chạy (từ thư mục gốc của dự án):  python test_golden.py
Mỗi dòng kết quả là PASS (đúng) / FAIL (sai, kèm chi tiết) / TODO (chưa cài đặt).

Các ví dụ nằm trong thư mục cases/ (mỗi file một ví dụ, biến CASE).
Muốn thêm ví dụ: tạo file mới cases/<ten_ban>_<so>.py, KHÔNG sửa file của người khác.
"""
import importlib
import pkgutil
import sys

import cases
from gadget import assemble_gadget
from keypoint import extract_key_points
from pipeline import run_pipeline
from slicer import build_slices
from vdp_contract import KeyPoint, Slice, Statement

# recv là forward theo bài báo; hướng các hàm khác nhóm tự chốt trong api_list.json.
API_LIST = {"strcpy": "backward", "recv": "forward"}

CASES = [importlib.import_module(f"cases.{m.name}").CASE
         for m in sorted(pkgutil.iter_modules(cases.__path__), key=lambda m: m.name)]


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
    got = extract_key_points(case["source"], API_LIST)
    want = _kp(case["key_point"])
    assert len(got) == 1, f"mong đợi 1 Key Point, nhận {len(got)}"
    k = got[0]
    assert (k.api, k.func, k.line, tuple(k.args), k.direction) == \
           (want.api, want.func, want.line, want.args, want.direction), \
           f"mong đợi {want}, nhận {k}"


def test_slices(case):
    kp = _kp(case["key_point"])  # Key Point chuẩn làm đầu vào
    got = build_slices(case["source"], kp)
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
    g = assemble_gadget(kp, slices)
    assert _pairs(g.statements) == case["gadget"], \
        f"mong đợi {case['gadget']}, nhận {_pairs(g.statements)}"


def test_pipeline(case):
    gs = run_pipeline(case["source"], API_LIST)
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
