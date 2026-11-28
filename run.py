import ast
import sys
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

for step in steps:
    print(step)
for i, call in enumerate(calls):
    print(i, call)