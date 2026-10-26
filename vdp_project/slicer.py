
"""Member B - Step I.2: Generate program slices."""

import re
from typing import List, Set, Tuple

from vdp_contract import KeyPoint, Slice, Statement


ID = re.compile(r"\b[A-Za-z_]\w*\b")
CALL = re.compile(r"\b([A-Za-z_]\w*)\s*\(([^()]*)\)")
HEADER = re.compile(r"\b([A-Za-z_]\w*)\s*\(([^()]*)\)\s*\{")

KEYWORDS = set("""
auto break case char const continue default do double else enum extern
float for goto if int long register return short signed sizeof static
struct switch typedef union unsigned void volatile while _Bool
""".split())

CONTROL = {"if", "else", "for", "while", "switch", "return", "sizeof"}


def clean(text):
    text = re.sub(r"/\*.*?\*/", "", text)
    return re.sub(r"//.*", "", text).strip()


def ids(text):
    return {x for x in ID.findall(text) if x not in KEYWORDS}


def split_args(text):
    result, start, depth = [], 0, 0
    if not text.strip():
        return ()

    for i, c in enumerate(text):
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth = max(0, depth - 1)
        elif c == "," and depth == 0:
            result.append(text[start:i].strip())
            start = i + 1

    result.append(text[start:].strip())
    return tuple(result)


def parse_functions(source):
    lines = source.splitlines()
    text = "\n".join(lines)
    functions = []

    for m in HEADER.finditer(text):
        name = m.group(1)
        if name in CONTROL:
            continue

        prefix = text[:m.start()]
        boundary = max(prefix.rfind(";"), prefix.rfind("{"), prefix.rfind("}"))
        if "=" in prefix[boundary + 1:]:
            continue

        pos, depth = m.end(), 1
        while pos < len(text) and depth:
            depth += (text[pos] == "{") - (text[pos] == "}")
            pos += 1
        if depth:
            continue

        params = []
        for p in split_args(m.group(2)):
            if p.strip() == "void":
                continue
            names = [x for x in ID.findall(p) if x not in KEYWORDS]
            if names:
                params.append(names[-1])

        functions.append({
            "name": name,
            "start": text.count("\n", 0, m.start()) + 1,
            "end": min(text.count("\n", 0, pos) + 1, len(lines)),
            "signature": text.count("\n", 0, m.start(1)) + 1,
            "params": params,
        })

    return lines, functions


def analyze(text):
    """Trả về (biến được định nghĩa, biến được sử dụng)."""
    text = clean(text)

    if not text or text.startswith("#"):
        return set(), set()
    if re.match(r"^(if|else|for|while|switch)\b", text):
        return set(), set()

    assignment = re.search(
        r"(?<![=!<>])(?:\+=|-=|\*=|/=|%=|=(?!=))", text
    )

    if assignment:
        lhs, rhs = text[:assignment.start()], text[assignment.end():]
        names = [x for x in ID.findall(lhs) if x not in KEYWORDS]
        defined = {names[-1]} if names else set()
        return defined, ids(rhs) | (ids(lhs) - defined)

    declaration = re.match(
        r"^(?:(?:const|unsigned|signed)\s+)*"
        r"(?:char|short|int|long|float|double|void|_Bool)"
        r"\s+(.+);\s*$",
        text,
    )

    if declaration:
        first = split_args(declaration.group(1))[0]
        names = [x for x in ID.findall(first) if x not in KEYWORDS]
        defined = {names[0]} if names else set()
        uses = ids(re.sub(r"\b" + re.escape(next(iter(defined), "")) +
                          r"\b", "", first)) if defined else set()
        return defined, uses

    return set(), ids(text)


def build_slices(source: str, kp: KeyPoint) -> List[Slice]:
    lines, functions = parse_functions(source)
    by_name = {f["name"]: f for f in functions}

    if kp.func not in by_name:
        return []

    statements = {}
    lookup = {}

    for f in functions:
        name = f["name"]
        statements[name] = []

        for line in range(f["start"], f["end"] + 1):
            text = clean(lines[line - 1])

            if not text or text in {"{", "}"}:
                continue
            if re.match(r"^(if|else|for|while|switch)\b", text):
                continue

            st = Statement(name, line, lines[line - 1].strip())
            statements[name].append(st)
            lookup[(name, line)] = st

    def calls_in(text):
        return [
            (name, split_args(args))
            for name, args in CALL.findall(clean(text))
            if name not in CONTROL
        ]

    def trace(func, var, before, selected, visited):
        state = (func, var, before)
        if state in visited:
            return
        visited.add(state)

        # Tìm định nghĩa gần nhất của biến.
        for st in reversed(statements.get(func, [])):
            if st.line >= before:
                continue

            defs, uses = analyze(st.text)
            if var not in defs:
                continue

            selected.add((func, st.line))

            # Giữ khai báo riêng đứng trước phép gán.
            for prev in statements[func]:
                if prev.line >= st.line:
                    break
                if re.match(
                    r"^(?:(?:const|unsigned|signed)\s+)*"
                    r"(?:char|short|int|long|float|double|void|_Bool)\s+"
                    r"(?:\*\s*)*" + re.escape(var) + r"\b"
                    r"\s*(?:\[[^\]]*\])?\s*;",
                    clean(prev.text),
                ):
                    selected.add((func, prev.line))

            for used in uses:
                trace(func, used, st.line, selected, visited)
            return

        # Nếu là tham số hàm, truy ngược qua caller.
        f = by_name[func]
        if var not in f["params"]:
            return

        index = f["params"].index(var)

        for caller in functions:
            for st in statements[caller["name"]]:
                for call, args in calls_in(st.text):
                    if call != func or index >= len(args):
                        continue

                    selected.add((caller["name"], st.line))

                    # Chỉ thêm chữ ký callee nếu tham số của nó
                    # thực sự thuộc chuỗi phụ thuộc.
                    selected.add((func, f["signature"]))

                    for used in ids(args[index]):
                        trace(
                            caller["name"], used, st.line,
                            selected, visited,
                        )

    def function_order(selected):
        """Sắp xếp hàm theo quan hệ caller -> callee."""
        names = {name for name, _ in selected}
        edges = {name: set() for name in names}
        indegree = {name: 0 for name in names}

        for caller in names:
            for st in statements.get(caller, []):
                if (caller, st.line) not in selected:
                    continue

                for callee, _ in calls_in(st.text):
                    if callee in names and callee != caller:
                        if callee not in edges[caller]:
                            edges[caller].add(callee)
                            indegree[callee] += 1

        source_order = {
            f["name"]: i for i, f in enumerate(functions)
        }
        ready = sorted(
            [n for n in names if indegree[n] == 0],
            key=lambda n: source_order.get(n, 999),
        )
        result = []

        while ready:
            name = ready.pop(0)
            result.append(name)

            for callee in sorted(
                edges[name],
                key=lambda n: source_order.get(n, 999),
            ):
                indegree[callee] -= 1
                if indegree[callee] == 0:
                    ready.append(callee)
                    ready.sort(key=lambda n: source_order.get(n, 999))

        result.extend(n for n in sorted(
            names, key=lambda n: source_order.get(n, 999)
        ) if n not in result)

        return result

    slices = []

    for arg in kp.args:
        selected = {(kp.func, kp.line)}

        if kp.direction == "backward":
            visited = set()
            for var in ids(arg):
                trace(kp.func, var, kp.line, selected, visited)

            order = function_order(selected)
            pairs = [
                (name, line)
                for name in order
                for func_name, line in sorted(selected, key=lambda x: x[1])
                if func_name == name and (name, line) != (kp.func, kp.line)
            ]
            pairs.append((kp.func, kp.line))

        else:
            pairs = [(kp.func, kp.line)]
            pending = list(ids(arg))
            visited = set()

            while pending:
                var = pending.pop()
                if var in visited:
                    continue
                visited.add(var)

                for st in statements[kp.func]:
                    if st.line <= kp.line:
                        continue
                    defs, uses = analyze(st.text)
                    if var in uses:
                        selected.add((kp.func, st.line))
                        pending.extend(defs - visited)

            pairs.extend(sorted(
                selected - {(kp.func, kp.line)},
                key=lambda x: x[1],
            ))

        slices.append(Slice(
            key_point=kp,
            arg=arg,
            direction=kp.direction,
            statements=tuple(
                lookup[p] for p in pairs if p in lookup
            ),
        ))

    return slices
