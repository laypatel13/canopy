import ast
from html import escape

code = "total = price * 2 + tax"
tree = ast.parse(code)

leaves = []
x = {}
y = {}

def visit(node):
    if isinstance(node, ast.Name) or isinstance(node, ast.Constant):
        leaves.append(node)
    for child in ast.iter_child_nodes(node):
        visit(child)

def label(node):
    if isinstance(node, ast.Name):
        return node.id
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
            parts.append(f'<line x1="{sx(node)}" y1="{sy(node)}" x2="{sx(child)}" y2="{sy(child)}" stroke="#ece7de" stroke-width="2"/>')

for leaf in leaves:
    if isinstance(leaf, ast.Name):
        colour = "#4fd08b"
    else:
        colour = "#ece7de"
    word = escape(str(label(leaf)))
    parts.append(f'<text x="{sx(leaf)}" y="{sy(leaf) - 16}" fill="{colour}" font-family="monospace" font-size="18" text-anchor="middle">{word}</text>')

parts.append('</svg>')

with open("poster.svg", "w") as f:
    f.write("\n".join(parts))
