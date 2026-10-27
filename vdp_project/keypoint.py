"""Thành viên A - Step I.1: trích xuất Key Point (lời gọi hàm API). Chỉ sửa file này."""
from typing import List, Optional

import tree_sitter_c as tsc
from tree_sitter import Language, Parser

from vdp_contract import ApiList, KeyPoint

_parser = Parser(Language(tsc.language()))


def _enclosing_func(node) -> Optional[str]:
    """Đi lên function_definition, rồi đi xuống theo trường declarator tới identifier."""
    
    while node is not None and node.type != "function_definition":
        node = node.parent
    if node is None:
        return None  # ngoài mọi hàm -> bỏ (Q9)
    d = node.child_by_field_name("declarator")
    while d is not None and d.type != "identifier":
        d = d.child_by_field_name("declarator")
    return d.text.decode("utf-8") if d is not None else None


def extract_key_points(source: str, api_list: ApiList) -> List[KeyPoint]:
    """Trả về các KeyPoint theo thứ tự dòng tăng dần (xem quy ước Q1-Q9 trong vdp_contract.py)."""
    tree = _parser.parse(source.encode("utf-8"))
    result: List[KeyPoint] = []

    def walk(node):
        if node.type == "call_expression":
            fn = node.child_by_field_name("function")
            if fn is not None and fn.type == "identifier":      # Q9
                name = fn.text.decode("utf-8")
                if name in api_list:                            # Q6
                    func = _enclosing_func(node)
                    if func is not None:
                        args_node = node.child_by_field_name("arguments")
                        args = tuple(
                            c.text.decode("utf-8")
                            for c in args_node.named_children
                            if c.type != "comment"
                        )
                        result.append(KeyPoint(
                            api=name,
                            func=func,
                            line=fn.start_point[0] + 1,         # Q8
                            args=args,
                            direction=api_list[name],
                        ))
        for c in node.children:
            walk(c)

    walk(tree.root_node)
    result.sort(key=lambda k: k.line)
    return result