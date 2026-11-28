import ast
import json
import sys
from pathlib import Path
from typing import List, Optional

number = sys.argv[1]
given = sys.argv[2]
code = sys.stdin.read()

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def parse(given):
    for word, py in [("null", "None"), ("true", "True"), ("false", "False")]:
        given = given.replace(word, py)
    call = ast.parse(f"f({given})").body[0].value
    inputs = {}
    for k in call.keywords:
        inputs[k.arg] = ast.literal_eval(k.value)
    return inputs

def build(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

def find_function(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node

func = find_function(ast.parse(code))
space = {"TreeNode": TreeNode, "Optional": Optional, "List": List}
exec(compile(code, "<solution>", "exec"), space)
solve = getattr(space["Solution"](), func.name)
inputs = parse(given)

for arg in func.args.args:
    if arg.annotation is not None and "TreeNode" in ast.unparse(arg.annotation):
        inputs[arg.arg] = build(inputs[arg.arg])

def show(value):
    if isinstance(value, TreeNode):
        return f"node {value.val}"
    return repr(value)

steps = []
calls = []
stack = []

def tracer(frame, event, arg):
    if frame.f_code.co_filename != "<solution>":
        return None
    if frame.f_code.co_name.startswith("<"):
        return None
    if event == "call":
        if stack:
            parent = stack[-1]
        else:
            parent = None
        calls.append({"parent": parent, "returned": None})
        stack.append(len(calls) - 1)
    me = stack[-1]
    if event == "return":
        calls[me]["returned"] = show(arg)
    seen = {}
    for name, value in frame.f_locals.items():
        if name != "self":
            seen[name] = show(value)
    steps.append({"event": event, "line": frame.f_lineno, "call": me, "locals": seen})
    if event == "return":
        stack.pop()
    return tracer

sys.settrace(tracer)
answer = solve(**inputs)
sys.settrace(None)

children = []
for call in calls:
    children.append([])
for i, call in enumerate(calls):
    if call["parent"] is not None:
        children[call["parent"]].append(i)

x = {}
y = {}

leaf = 0
for i in range(len(calls)):
    if not children[i]:
        x[i] = leaf
        leaf += 1

def place(i):
    if not children[i]:
        return [x[i]]
    xs = []
    for child in children[i]:
        xs += place(child)
    x[i] = sum(xs) / len(xs)
    return xs

def set_depth(i, depth):
    y[i] = depth
    for child in children[i]:
        set_depth(child, depth + 1)

place(0)
set_depth(0, 0)

for i, call in enumerate(calls):
    call["x"] = x[i]
    call["depth"] = y[i]

doc = ast.get_docstring(func)
summary = ""
if doc is not None:
    summary = doc.splitlines()[0]

data = {
    "name": func.name,
    "number": number,
    "given": given,
    "summary": summary,
    "code": code,
    "steps": steps,
    "calls": calls,
    "answer": show(answer),
}

player = Path(__file__).parent / "player.html"
page = player.read_text().replace("/*DATA*/", json.dumps(data).replace("</", "<\\/"))

with open(f"{number}.html", "w") as f:
    f.write(page)