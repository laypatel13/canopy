import ast
from html import escape
import inspect, shlex

code = inspect.getsource(shlex.quote)
tree = ast.parse(code)

func = tree.body[0]
doc = ast.get_docstring(func)
if doc is not None:
    func.body = func.body[1:]

leaves = []
x = {}
y = {}

def is_leaf(node):
    return isinstance(node, (ast.Name, ast.Constant, ast.arg))

def visit(node):
    if is_leaf(node):
        leaves.append(node)
    for child in ast.iter_child_nodes(node):
        visit(child)

def label(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.arg):
        return node.arg
    return node.value

def place(node):
    if node in x:
        return x[node]
    xs = []
    for child in ast.iter_child_nodes(node):
        cx = place(child)
        if cx is not None:
            xs.append(cx)
    if len(xs) == 0:
        return None
    x[node] = sum(xs) / len(xs)
    return x[node]

def set_depth(node, depth):
    if node in x:
        y[node] = depth
    for child in ast.iter_child_nodes(node):
        set_depth(child, depth + 1)

visit(tree)

for i, leaf in enumerate(leaves):
    x[leaf] = i

place(tree)
set_depth(tree, 0)

leaf_ys = []
for leaf in leaves:
    leaf_ys.append(y[leaf])
top = max(leaf_ys)

for leaf in leaves:
    y[leaf] = top

def count(node):
    if is_leaf(node):
        return 1
    num = 0
    for child in ast.iter_child_nodes(node):
        num += count(child)
    return num

GAP_X = 120
GAP_Y = 70
PAD = 80

def sx(node):
    return PAD + x[node] * GAP_X

def sy(node):
    return PAD + (top - y[node]) * GAP_Y

width = PAD * 2 + (len(leaves) - 1) * GAP_X
height = PAD * 2 + top * GAP_Y

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append(f'<rect width="{width}" height="{height}" fill="#0e0e0d"/>')

for node in x:
    for child in ast.iter_child_nodes(node):
        if child in x:
            w = count(child) * 2
            parts.append(f'<line x1="{sx(node)}" y1="{sy(node)}" x2="{sx(child)}" y2="{sy(child)}" stroke="#ece7de" stroke-width="{w}" stroke-linecap="round"/>')

for leaf in leaves:
    if isinstance(leaf, ast.Constant):
        colour = "#ece7de"
    else:
        colour = "#4fd08b"
    word = escape(str(label(leaf)))
    parts.append(f'<text x="{sx(leaf)}" y="{sy(leaf) - 16}" fill="{colour}" font-family="monospace" font-size="18" text-anchor="middle">{word}</text>')

parts.append('</svg>')

with open("poster.svg", "w") as f:
    f.write("\n".join(parts))
