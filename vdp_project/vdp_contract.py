"""
HỢP ĐỒNG CHUNG cho 3 module của nhóm:  Key Point -> Slicing -> Code Gadget

File này CHỈ chứa quy ước và kiểu dữ liệu. Không ai cài đặt thuật toán trong file này.
Sửa file này (kể cả đổi tên một trường) phải được cả 3 thành viên đồng ý
(qua Pull Request có đủ 3 người xem), rồi cập nhật lại các ví dụ trong thư mục cases/.

Mỗi người chỉ sửa file của mình:
  Thành viên A: keypoint.py  -> extract_key_points()  (bài báo: Step I.1, dễ nhất)
  Thành viên B: slicer.py    -> build_slices()        (bài báo: Step I.2, khó nhất)
  Thành viên C: gadget.py    -> assemble_gadget()     (bài báo: Step II.1, mức vừa)
"""
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

Direction = Literal["forward", "backward"]

# api_list: {tên hàm API: hướng}. Ví dụ {"strcpy": "backward", "recv": "forward"}.
# Danh sách tên hàm lấy từ Table VII (Appendix B) của bài báo; hướng forward/backward
# của từng hàm do nhóm tự chốt trong một file api_list.json dùng chung (người A soạn).
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
# Q8. "line" của một lời gọi = dòng chứa TÊN HÀM được gọi (dòng bắt đầu của lời gọi).
#     "args" = văn bản của từng đối số, bỏ qua comment nằm trong ngoặc.
# Q9. Bỏ qua lời gọi mà tên hàm không phải một định danh đơn giản (ví dụ obj->read(...),
#     con trỏ hàm) và lời gọi nằm ngoài mọi hàm (ví dụ khởi tạo biến toàn cục).
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
    line: int               # dòng của lời gọi (xem Q8)
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
