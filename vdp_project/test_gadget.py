"""Test bổ sung cho gadget.py (thành viên C). Chạy: python test_gadget.py"""
from gadget import assemble_gadget
from vdp_contract import KeyPoint, Slice, Statement

KP = KeyPoint("strcpy", "test", 9, ("buf", "str"), "backward")


def S(func, line):
    return Statement(func, line, f"{func}:{line}")


def sl(arg, *pairs):
    return Slice(KP, arg, "backward", tuple(S(f, l) for f, l in pairs))


def pairs(g):
    return [(s.func, s.line) for s in g.statements]


def test_dedupe_and_sort():
    g = assemble_gadget(KP, [sl("a", ("t", 9), ("t", 4), ("t", 9)), sl("b", ("t", 5), ("t", 9))])
    assert pairs(g) == [("t", 4), ("t", 5), ("t", 9)]


def test_caller_before_callee_even_if_listed_late():
    # slice của buf (chỉ test) đứng trước slice của str (main -> test)
    g = assemble_gadget(KP, [sl("buf", ("test", 4), ("test", 9)),
                             sl("str", ("main", 18), ("test", 2), ("test", 9))])
    assert [f for f, _ in pairs(g)] == ["main", "test", "test", "test"]


def test_no_ordering_info_uses_first_appearance():
    g = assemble_gadget(KP, [sl("a", ("zeta", 1)), sl("b", ("alpha", 2))])
    assert pairs(g) == [("zeta", 1), ("alpha", 2)]


def test_cycle_is_deterministic():
    a = [sl("x", ("f", 1), ("g", 5)), sl("y", ("g", 6), ("f", 2))]
    assert pairs(assemble_gadget(KP, a)) == pairs(assemble_gadget(KP, a))
    assert pairs(assemble_gadget(KP, a)) == [("f", 1), ("f", 2), ("g", 5), ("g", 6)]


def test_three_level_chain():
    g = assemble_gadget(KP, [sl("a", ("c", 3), ("c", 4)),
                             sl("b", ("a", 1), ("b", 2), ("c", 3))])
    assert [f for f, _ in pairs(g)] == ["a", "b", "c", "c"]


def test_empty_and_label():
    g = assemble_gadget(KP, [])
    assert g.statements == [] and g.label is None and g.key_point == KP


def test_input_not_modified():
    s1 = sl("a", ("t", 9), ("t", 4))
    before = s1.statements
    assemble_gadget(KP, [s1])
    assert s1.statements == before


if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); n += 1; print("PASS", name)
    print(f"{n} test đạt")
