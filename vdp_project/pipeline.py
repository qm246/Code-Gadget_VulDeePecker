"""Ghép cả 3 module. Dùng được khi cả ba đã xong."""
from typing import List

from gadget import assemble_gadget
from keypoint import extract_key_points
from slicer import build_slices
from vdp_contract import ApiList, CodeGadget


def run_pipeline(source: str, api_list: ApiList) -> List[CodeGadget]:
    return [assemble_gadget(kp, build_slices(source, kp))
            for kp in extract_key_points(source, api_list)]
