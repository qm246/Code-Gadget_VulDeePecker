
"""Member B - Generate program slices."""

import re
from typing import List

from vdp_contract import KeyPoint, Slice, Statement


ID = re.compile(r"\b[A-Za-z_]\w*\b")
HEADER = re.compile(r"\b([A-Za-z_]\w*)\s*\(([^()]*)\)\s*\{")
CALL = re.compile(r"\b([A-Za-z_]\w*)\s*\(([^()]*)\)")
ASSIGN = re.compile(r"(?<![=!<>])(?:\+=|-=|\*=|/=|%=|=(?!=))")

KEYWORDS = set("""
auto break case char const continue default do double else enum extern
float for goto if int long register return short signed sizeof static
struct switch typedef union unsigned void volatile while _Bool
""".split())

CONTROL = {"if", "else", "for", "while", "switch", "return", "sizeof"}
TYPE = r"(?:char|short|int|long|float|double|void|_Bool)"


def clean(text):
    text = re.sub(r"/\*.*?\*/", "", text)
    return re.sub(r"//.*", "", text).strip()


def ids(text):
    return {x for x in ID.findall(text) if x not in KEYWORDS}


def split_args(text):
    if not text.strip():
        return ()

    result = []
    start = 0
    depth = 0

    for i, char in enumerate(text):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            result.append(text[start:i].strip())
            start = i + 1

    result.append(text[start:].strip())
    return tuple(result)


def calls_in(text):
    return [
        (name, split_args(args))
        for name, args in CALL.findall(clean(text))
        if name not in CONTROL
    ]


def parse_functions(source):
    lines = source.splitlines()
    text = "\n".join(lines)
    functions = []
    occupied = []

    for match in HEADER.finditer(text):
        name = match.group(1)

        if name in CONTROL:
            continue

        prefix = text[:match.start()]
        boundary = max(
            prefix.rfind(";"),
            prefix.rfind("{"),
            prefix.rfind("}")
        )

        if "=" in prefix[boundary + 1:]:
            continue

        if any(start <= match.start() < end for start, end in occupied):
            continue

        pos = match.end()
        depth = 1

        while pos < len(text) and depth:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1

        if depth:
            continue

        params = []

        for param in split_args(match.group(2)):
            if param.strip() == "void":
                continue

            names = [
                x for x in ID.findall(param)
                if x not in KEYWORDS
            ]

            if names:
                params.append(names[-1])

        functions.append({
            "name": name,
            "start": text.count("\n", 0, match.start()) + 1,
            "end": min(
                text.count("\n", 0, pos) + 1,
                len(lines)
            ),
            "signature": text.count("\n", 0, match.start(1)) + 1,
            "params": params,
        })

        occupied.append((match.start(), pos))

    functions.sort(key=lambda f: f["start"])
    return lines, functions


def analyze(text):
    """Return the variables defined and used by a statement."""
    text = clean(text)

    if not text or text.startswith("#"):
        return set(), set()

    if re.match(r"^(if|else|for|while|switch)\b", text):
        return set(), set()

    assignment = ASSIGN.search(text)

    if assignment:
        lhs = text[:assignment.start()]
        rhs = text[assignment.end():]

        names = [
            x for x in ID.findall(lhs)
            if x not in KEYWORDS
        ]

        defined = {names[-1]} if names else set()
        used = ids(rhs) | (ids(lhs) - defined)

        return defined, used

    declaration = re.match(
        r"^(?:(?:const|unsigned|signed|static|volatile)\s+)*"
        + TYPE + r"\s+(.+);\s*$",
        text
    )

    if declaration:
        defined = set()
        used = set()

        for item in split_args(declaration.group(1)):
            left = item.split("=", 1)[0].strip()
            names = [
                x for x in ID.findall(left)
                if x not in KEYWORDS
            ]

            if not names:
                continue

            defined.add(names[0])

            if "=" in item:
                used |= ids(item.split("=", 1)[1])

            for array_size in re.findall(r"\[([^\]]*)\]", left):
                used |= ids(array_size)

        return defined, used

    return set(), ids(text)


def is_declaration(text, var):
    text = clean(text)

    return bool(re.match(
        r"^(?:(?:const|unsigned|signed|static|volatile)\s+)*"
        + TYPE + r"\s+(?:\*\s*)*"
        + re.escape(var)
        + r"\b\s*(?:\[[^\]]*\])?\s*(?:=[^;]*)?;",
        text
    ))


def build_slices(source: str, kp: KeyPoint) -> List[Slice]:
    lines, functions = parse_functions(source)
    by_name = {f["name"]: f for f in functions}

    if kp.func not in by_name:
        return []

    statements = {}
    lookup = {}

    for function in functions:
        name = function["name"]
        statements[name] = []

        for line_no in range(function["start"], function["end"] + 1):
            raw = lines[line_no - 1]
            text = clean(raw)

            if not text or text in {"{", "}"}:
                continue

            if re.match(r"^(if|else|for|while|switch)\b", text):
                continue

            statement = Statement(name, line_no, raw.strip())
            statements[name].append(statement)
            lookup[(name, line_no)] = statement

    def callers_of(func):
        result = []

        for caller in functions:
            caller_name = caller["name"]

            for statement in statements.get(caller_name, []):
                for called, args in calls_in(statement.text):
                    if called == func:
                        result.append((caller_name, statement, args))

        return result

    def previous_definition(func, var, before):
        for statement in reversed(statements.get(func, [])):
            if statement.line >= before:
                continue

            defined, used = analyze(statement.text)

            if var in defined:
                return statement, used

        return None, set()

    def backward(func, var, before, selected, visited):
        state = (func, var, before)

        if state in visited:
            return

        visited.add(state)

        definition, used = previous_definition(func, var, before)

        if definition:
            selected.add((func, definition.line))

            for statement in statements[func]:
                if statement.line >= definition.line:
                    break

                if is_declaration(statement.text, var):
                    selected.add((func, statement.line))

            for used_var in used:
                backward(
                    func, used_var, definition.line,
                    selected, visited
                )

            return

        function = by_name[func]

        if var not in function["params"]:
            return

        index = function["params"].index(var)

        for caller_name, call_statement, args in callers_of(func):
            if index >= len(args):
                continue

            selected.add((caller_name, call_statement.line))

            for arg_var in ids(args[index]):
                backward(
                    caller_name, arg_var, call_statement.line,
                    selected, visited
                )

    def forward(func, var, after, selected, visited):
        state = (func, var, after)

        if state in visited:
            return

        visited.add(state)

        for statement in statements.get(func, []):
            if statement.line <= after:
                continue

            defined, used = analyze(statement.text)

            if var not in used:
                continue

            selected.add((func, statement.line))

            for new_var in defined:
                forward(
                    func, new_var, statement.line,
                    selected, visited
                )

            for called, args in calls_in(statement.text):
                callee = by_name.get(called)

                if not callee:
                    continue

                for index, arg in enumerate(args):
                    if index >= len(callee["params"]):
                        continue

                    if var not in ids(arg):
                        continue

                    param = callee["params"][index]

                    # Theo dõi dữ liệu trong hàm được gọi.
                    # Không thêm dòng chữ ký hàm vào slice.
                    forward(
                        called, param, callee["signature"],
                        selected, visited
                    )

        function = by_name[func]

        if var not in function["params"]:
            return

        index = function["params"].index(var)

        for caller_name, call_statement, args in callers_of(func):
            if index >= len(args):
                continue

            arg_vars = ids(args[index])

            if not arg_vars:
                continue

            selected.add((caller_name, call_statement.line))

            for arg_var in arg_vars:
                forward(
                    caller_name, arg_var, call_statement.line,
                    selected, visited
                )

    slices = []

    for arg in kp.args:
        selected = {(kp.func, kp.line)}

        if kp.direction == "backward":
            visited = set()

            for var in ids(arg):
                backward(
                    kp.func, var, kp.line, selected, visited
                )

            names = {func for func, _ in selected}
            source_order = {
                f["name"]: i for i, f in enumerate(functions)
            }
            edges = {name: set() for name in names}
            indegree = {name: 0 for name in names}

            for caller in names:
                for statement in statements.get(caller, []):
                    if (caller, statement.line) not in selected:
                        continue

                    for callee, _ in calls_in(statement.text):
                        if (
                            callee in names
                            and callee != caller
                            and callee not in edges[caller]
                        ):
                            edges[caller].add(callee)
                            indegree[callee] += 1

            ready = sorted(
                [name for name in names if indegree[name] == 0],
                key=lambda name: source_order.get(name, 999)
            )
            order = []

            while ready:
                name = ready.pop(0)
                order.append(name)

                for callee in sorted(
                    edges[name],
                    key=lambda item: source_order.get(item, 999)
                ):
                    indegree[callee] -= 1

                    if indegree[callee] == 0:
                        ready.append(callee)
                        ready.sort(
                            key=lambda item: source_order.get(item, 999)
                        )

            order.extend(
                name for name in sorted(
                    names,
                    key=lambda item: source_order.get(item, 999)
                )
                if name not in order
            )

            pairs = [
                (func, line)
                for func in order
                for selected_func, line in sorted(
                    selected, key=lambda pair: pair[1]
                )
                if (
                    selected_func == func
                    and (func, line) != (kp.func, kp.line)
                )
            ]
            pairs.append((kp.func, kp.line))

        else:
            visited = set()

            for var in ids(arg):
                forward(
                    kp.func, var, kp.line, selected, visited
                )

            kp_pair = (kp.func, kp.line)
            remaining = selected - {kp_pair}

           # Chỉ loại chữ ký của hàm chứa key point.
# Giữ chữ ký của các hàm được gọi nếu chúng thuộc slice.
            remaining = {
                pair for pair in remaining
                if pair != (kp.func, by_name[kp.func]["signature"])
            }
            source_order = {
                f["name"]: i for i, f in enumerate(functions)
            }

            pairs = [kp_pair] + sorted(
                remaining,
                key=lambda pair: (
                    0 if pair[0] == "main" else 1,
                    pair[1] if pair[0] == "main"
                    else source_order.get(pair[0], 999),
                    pair[1],
                )
            )

        slices.append(Slice(
            key_point=kp,
            arg=arg,
            direction=kp.direction,
            statements=tuple(
                lookup[pair]
                for pair in pairs
                if pair in lookup
            ),
        ))

    return slices
