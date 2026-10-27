"""Ghép cả 3 module. Dùng được khi cả ba đã xong. Do thành viên C giữ file."""
import json
import sys
from typing import List

from gadget import assemble_gadget
from keypoint import extract_key_points
from slicer import build_slices
from vdp_contract import ApiList, CodeGadget


def run_pipeline(source: str, api_list: ApiList) -> List[CodeGadget]:
    return [assemble_gadget(kp, build_slices(source, kp))
            for kp in extract_key_points(source, api_list)]


def main(argv: List[str]) -> int:
    """Chạy thử trên file C thật:  python pipeline.py sample.c [api_list.json]"""
    if len(argv) < 2:
        print("Cách dùng: python pipeline.py <file.c> [api_list.json]")
        return 2
    api_path = argv[2] if len(argv) > 2 else "api_list.json"
    with open(api_path, encoding="utf-8") as f:
        api_list = json.load(f)
    with open(argv[1], encoding="utf-8") as f:
        source = f.read()
    for g in run_pipeline(source, api_list):
        kp = g.key_point
        print(f"Key Point: {kp.api} (dòng {kp.line}, hàm {kp.func})")
        for st in g.statements:
            print(f"  {st.func}:{st.line}  {st.text}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
