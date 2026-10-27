"""Thành viên C - Step II.1: ghép các slice thành Code Gadget. Chỉ sửa file này."""
from typing import Dict, List, Set, Tuple

from vdp_contract import CodeGadget, KeyPoint, Slice, Statement


def _function_order(slices: List[Slice]) -> List[str]:
    """Thứ tự các hàm trong gadget (Q5, bước 2). Kết quả xác định, không ngẫu nhiên.

    - Với mỗi slice, lấy dãy hàm theo thứ tự xuất hiện đầu tiên trong chuỗi
      (ví dụ main, main, test, test -> main, test). Hai hàm liền nhau trong dãy
      tạo một ràng buộc "hàm trước đứng trước hàm sau" (hàm gọi đứng trước hàm được gọi).
    - Sắp xếp topo (Kahn). Khi nhiều hàm cùng "sẵn sàng" hoặc gặp vòng
      (đệ quy, hai slice nói ngược nhau) thì chọn hàm xuất hiện sớm nhất trong
      danh sách slices.
    """
    first_seen: Dict[str, int] = {}          # hàm -> thứ tự xuất hiện đầu tiên
    edges: Set[Tuple[str, str]] = set()      # (trước, sau)

    for sl in slices:
        chain: List[str] = []
        for st in sl.statements:
            if st.func not in first_seen:
                first_seen[st.func] = len(first_seen)
            if st.func not in chain:
                chain.append(st.func)
        edges.update(zip(chain, chain[1:]))

    remaining = sorted(first_seen, key=first_seen.get)
    order: List[str] = []
    while remaining:
        ready = [f for f in remaining
                 if not any(b == f and a in remaining and a != f for a, b in edges)]
        pick = (ready or remaining)[0]       # remaining đã sắp theo first_seen
        order.append(pick)
        remaining.remove(pick)
    return order


def assemble_gadget(kp: KeyPoint, slices: List[Slice]) -> CodeGadget:
    """Chỉ dùng thông tin trong kp và slices (không đọc lại source). Xem quy ước Q5."""
    # Bước 1: gộp câu lệnh của mọi slice, nhóm theo hàm, bỏ trùng (func, line).
    by_func: Dict[str, Dict[int, Statement]] = {}
    for sl in slices:
        for st in sl.statements:
            by_func.setdefault(st.func, {}).setdefault(st.line, st)

    # Bước 2: thứ tự giữa các hàm. Bước 3: trong hàm sắp theo dòng tăng dần.
    statements: List[Statement] = []
    for func in _function_order(slices):
        statements.extend(by_func[func][ln] for ln in sorted(by_func[func]))

    return CodeGadget(key_point=kp, statements=statements, label=None)
