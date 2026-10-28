# Tái hiện Key Point → Slicing → Code Gadget (VulDeePecker)

Dự án NCKH tại Trường Đại học Công nghiệp Hà Nội (HaUI), khoa MMT&TT, GVHD: PGS. Lê Trọng Vĩnh.

Nhóm cài đặt lại ba bước đầu của hệ thống VulDeePecker: tìm lời gọi hàm API nghi vấn (Key Point), sinh program slice cho từng đối số, rồi ghép thành Code Gadget. Chương trình đọc một file mã nguồn C và in ra các code gadget. Các bước sau của bài báo (gán nhãn, vector hóa, mạng BLSTM) chưa nằm trong phạm vi.

Nguồn: Z. Li, D. Zou, S. Xu, X. Ou, H. Jin, S. Wang, Z. Deng, Y. Zhong, "VulDeePecker: A Deep Learning-Based System for Vulnerability Detection", NDSS 2018.

## Tài liệu
- Tổng kết khái niệm, ví dụ và liên hệ với sản phẩm: [docs/Summary_KeyPoint_Slicing_CodeGadget.docx](docs/Summary_KeyPoint_Slicing_CodeGadget.docx)

## Ví dụ chạy thử
File `vdp_project/sample1.c` có hai lời gọi API là `strcpy` (trong `greet`) và `memcpy` (trong `main`). Kết quả:

```
Key Point: strcpy (dòng 6, hàm greet)
  main:10  int main(int argc, char **argv) {
  main:13  greet(argv[1]);
  greet:4  void greet(char *name) {
  greet:5  char buf[16];
  greet:6  strcpy(buf, name);
Key Point: memcpy (dòng 12, hàm main)
  main:10  int main(int argc, char **argv) {
  main:11  char tmp[64];
  main:12  memcpy(tmp, argv[1], 8);
```

Mỗi lời gọi API cho đúng một code gadget.

## Thành viên và phần phụ trách
| Thành viên | Phần | File |
|---|---|---|
| Minh | Key Point (Step I.1) | `keypoint.py`, `api_list.json`, `test_keypoint.py` |
| Ngô Ngọc | Slicing (Step I.2) | `slicer.py` |
| Nguyễn Thế Tài | Code Gadget (Step II.1) | `gadget.py`, `pipeline.py` |

## Cấu trúc repo
- `docs/`: tài liệu tổng kết.
- `vdp_project/`: mã nguồn. `vdp_contract.py` (quy ước và kiểu dữ liệu chung), `cases/` (các ví dụ chuẩn), `test_golden.py` (test chuẩn).

## Cài đặt và chạy

Chạy test: `python test_golden.py` (PASS / FAIL / TODO).

Chạy demo: python pipeline.py sample1.c

