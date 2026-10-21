# Tái hiện Key Point -> Slicing -> Code Gadget (bài báo VulDeePecker)

## Cấu trúc và ai sửa file nào
| File | Vai trò | Ai sửa |
|---|---|---|
| `vdp_contract.py` | quy ước + kiểu dữ liệu chung | chỉ khi cả 3 đồng ý (qua Pull Request) |
| `keypoint.py` | tìm Key Point (Step I.1) | Thành viên A |
| `slicer.py` | sinh slice (Step I.2) | Thành viên B |
| `gadget.py` | ghép Code Gadget (Step II.1) | Thành viên C |
| `pipeline.py` | ghép 3 module | sau khi cả ba xong |
| `test_golden.py` | chạy test chuẩn | chỉ khi cả 3 đồng ý |
| `cases/` | mỗi file là một ví dụ chuẩn | ai cũng được THÊM file mới của mình |

## Cài đặt (mỗi máy làm một lần)
```
python -m venv venv
venv\Scripts\activate            # Windows (cmd/PowerShell)
source venv/Scripts/activate     # Windows (Git Bash)
source venv/bin/activate         # macOS / Linux
pip install -r requirements.txt
```
Nếu pip báo không có bản cài cho phiên bản Python của bạn, dùng Python 3.11 - 3.13.
Cả nhóm nên dùng cùng một phiên bản Python.

## Chạy test
```
python test_golden.py
```
- `PASS`: đúng. `FAIL`: sai (kèm "mong đợi" và "nhận"). `TODO`: chưa cài đặt.
- Mỗi người chỉ cần làm dòng của mình thành PASS ở mọi ví dụ.

## Làm việc với Git (không sửa code trực tiếp trên trang GitHub)
```
git clone <đường dẫn repo>
cd <thư mục repo>
git checkout -b keypoint          # B: slicing, C: gadget
# ... sửa file của mình, chạy python test_golden.py ...
git add keypoint.py
git commit -m "Key Point: mô tả ngắn việc đã làm"
git push -u origin keypoint
```
Rồi vào GitHub bấm "Compare & pull request", nhờ một bạn xem, bấm Merge vào `main`.
Muốn lấy phần của bạn khác đã merge: `git checkout main` rồi `git pull`.

## Quy tắc chung
1. Chỉ sửa file của mình. Muốn đổi quy ước hoặc kiểu dữ liệu thì bàn cả nhóm trước.
2. Không đẩy thẳng lên `main`; luôn qua nhánh riêng + Pull Request.
3. Chỉ merge khi `python test_golden.py` không có `FAIL` ở phần của mình.
4. Thêm ví dụ mới: tạo `cases/<ten_ban>_<so>.py` theo mẫu `cases/fig3_paper.py`,
   rồi nhờ người khác duyệt đáp án.
