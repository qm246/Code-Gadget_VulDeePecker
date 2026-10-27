"""Test riêng cho thành viên A (Key Point). Chạy: python test_keypoint.py"""
import json
import os

from keypoint import extract_key_points

API = {"strcpy": "backward", "strdup": "backward", "recv": "forward"}


def test_comment_va_chuoi():
    src = 'void f(){ // strcpy(a,b)\n  char *s = "strcpy(a,b)";\n  /* strcpy(a,b) */\n}'
    assert extract_key_points(src, API) == []


def test_con_tro_ham_va_obj():
    src = "void f(){ obj->strcpy(a,b); (*strcpy)(a,b); }"
    assert extract_key_points(src, API) == []


def test_ngoai_ham():
    assert extract_key_points("int x = strcpy(a,b);", API) == []


def test_ham_tra_ve_con_tro():
    src = "char *dup(char *s){ char b[8]; strcpy(b,s); return b; }"
    kps = extract_key_points(src, API)
    assert len(kps) == 1 and kps[0].func == "dup"


def test_long_nhau():
    src = "void f(){\n  strcpy(buf, strdup(s));\n}"
    kps = extract_key_points(src, API)
    assert [k.api for k in kps] == ["strcpy", "strdup"]
    assert kps[0].line == kps[1].line == 2


def test_args_tuple_bo_comment_nhieu_dong():
    src = "void f(){\n  strcpy(a, /* ghi chu */ b);\n  recv(0,\n       a, 8, 0);\n}"
    kps = extract_key_points(src, API)
    assert kps[0].args == ("a", "b") and isinstance(kps[0].args, tuple)
    assert (kps[1].api, kps[1].line, kps[1].args, kps[1].direction) == \
           ("recv", 3, ("0", "a", "8", "0"), "forward")


def test_sap_theo_dong():
    src = "void f(){\n  recv(0,a,8,0);\n  strcpy(a,b);\n}"
    assert [k.line for k in extract_key_points(src, API)] == [2, 3]


def test_api_list_json():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_list.json")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    assert d["strcpy"] == "backward" and d["recv"] == "forward"
    assert set(d.values()) <= {"forward", "backward"}


def main():
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    n_fail = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            n_fail += 1
            print(f"  FAIL  {name}: {e}")
    print(f"\n{len(tests) - n_fail}/{len(tests)} test đạt")
    raise SystemExit(1 if n_fail else 0)


if __name__ == "__main__":
    main()