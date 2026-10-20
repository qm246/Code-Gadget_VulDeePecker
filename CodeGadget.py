"""
HỢP ĐỒNG CHUNG cho 3 module của nhóm:  Key Point -> Slicing -> Code Gadget

Cách dùng file này
- Đây là file DUY NHẤT định nghĩa kiểu dữ liệu trao đổi giữa các module.
- Sửa file này (kể cả đổi tên một trường) phải được cả 3 thành viên đồng ý,
  rồi cập nhật lại test_golden.py.
- Mỗi người chỉ cài đặt hàm của mình (thay dòng NotImplementedError),
  KHÔNG sửa kiểu dữ liệu.

Phân công gợi ý (tương ứng các bước trong bài báo)
  Thành viên A: extract_key_points()  - Step I.1  (dễ nhất)
  Thành viên B: build_slices()        - Step I.2  (khó nhất)
  Thành viên C: assemble_gadget()     - Step II.1 (mức vừa)
"""
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

Direction = Literal["forward", "backward"]

# api_list: {tên hàm API: hướng}. Ví dụ {"strcpy": "backward", "recv": "forward"}.
# Danh sách tên hàm lấy từ Table VII (Appendix B) của bài báo; hướng forward/backward
# của từng hàm do nhóm tự chốt trong một file api_list.json dùng chung.
ApiList = Dict[str, Direction]

# =====================  QUY ƯỚC ĐÃ CHỐT (cả nhóm phải theo)  =====================
# Q1. Đầu vào là một file C (chuỗi source). Số dòng đếm từ 1, theo file GỐC.
# Q2. Một "câu lệnh" = một dòng. Riêng chữ ký hàm: lấy dòng chứa TÊN HÀM và danh sách
#     tham số (ví dụ "void\ntest(char *str)" -> dòng 2, không phải dòng 1), khớp Figure 3.
# Q3. Chỉ xét DATA dependency, giống bản cài đặt của bài báo. Dòng điều kiện kiểu
#     "if (...)" KHÔNG đưa vào slice. (Control dependency có thể làm tùy chọn mở rộng
#     sau này, mặc định TẮT, và không nằm trong test chuẩn.)
# Q4. Slice là một chuỗi (chain) câu lệnh và luôn chứa dòng của Key Point.
#     Backward slice kết thúc bằng dòng Key Point; forward slice bắt đầu bằng dòng đó.
# Q5. Ghép Gadget:
#     (1) gộp các slice của cùng một lời gọi, nhóm theo hàm, sắp theo số dòng tăng dần,
#         bỏ dòng trùng;
#     (2) nối các hàm lại: nếu các chuỗi slice đã cho thứ tự giữa hai hàm (hàm gọi đứng
#         trước hàm được gọi) thì giữ thứ tự đó; nếu không có thì theo thứ tự xuất hiện
#         đầu tiên trong danh sách slices (xác định, KHÔNG ngẫu nhiên như bài báo,
#         để kết quả tái lập được).
# Q6. Key Point chỉ là lời gọi hàm có tên trong api_list. Lời gọi hàm tự định nghĩa
#     (như test(...)) bị bỏ qua.
# Q7. Khi so sánh trong test chỉ so (func, line), không so nội dung dòng.
# =================================================================================


@dataclass(frozen=True)
class Statement:
    func: str  # tên hàm người dùng chứa dòng này
    line: int  # số dòng (từ 1)
    text: str  # nội dung dòng, đã strip


@dataclass(frozen=True)
class KeyPoint:
    api: str                # tên hàm API, ví dụ "strcpy"
    func: str               # hàm người dùng chứa lời gọi, ví dụ "test"
    line: int               # dòng của lời gọi
    args: Tuple[str, ...]   # các đối số, ví dụ ("buf", "str")
    direction: Direction    # tra từ api_list


@dataclass(frozen=True)
class Slice:
    key_point: KeyPoint
    arg: str                           # đối số mà slice này theo dõi
    direction: Direction
    statements: Tuple[Statement, ...]  # theo thứ tự chuỗi (chain)


@dataclass
class CodeGadget:
    key_point: KeyPoint
    statements: List[Statement]
    label: Optional[int] = None  # 1/0; gán ở bước gán nhãn sau, mặc định None


# =====================  GIAO DIỆN 3 MODULE  =====================

def extract_key_points(source: str, api_list: ApiList) -> List[KeyPoint]:
    """Thành viên A. Trả về các KeyPoint theo thứ tự dòng tăng dần."""
    raise NotImplementedError("Thành viên A chưa cài đặt")


def build_slices(source: str, kp: KeyPoint) -> List[Slice]:
    """Thành viên B. Mỗi đối số của kp cho ít nhất một Slice;
    kp.direction quyết định đó là forward hay backward slice."""
    raise NotImplementedError("Thành viên B chưa cài đặt")


def assemble_gadget(kp: KeyPoint, slices: List[Slice]) -> CodeGadget:
    """Thành viên C. Chỉ dùng thông tin trong kp và slices (không đọc lại source)."""
    raise NotImplementedError("Thành viên C chưa cài đặt")


def run_pipeline(source: str, api_list: ApiList) -> List[CodeGadget]:
    """Ghép cả 3 module. Dùng được khi cả ba đã xong."""
    gadgets = []
    for kp in extract_key_points(source, api_list):
        gadgets.append(assemble_gadget(kp, build_slices(source, kp)))
    return gadgets
