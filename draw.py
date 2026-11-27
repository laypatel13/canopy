import ast
from html import escape
import inspect, shlex
import math
import os
import platform

code = inspect.getsource(shlex.quote)
tree = ast.parse(code)

func = tree.body[0]
doc = ast.get_docstring(func)
if doc is not None:
    func.body = func.body[1:]

name = func.name
summary = doc.splitlines()[0]
file = os.path.basename(inspect.getsourcefile(shlex.quote))
line = inspect.getsourcelines(shlex.quote)[1]
ground = f"cpython {platform.python_version()} · Lib/{file} · line {line}"

leaves = []
x = {}
y = {}

def is_leaf(node):
    return isinstance(node, (ast.Name, ast.Constant, ast.arg, ast.Attribute))

def visit(node):
    if is_leaf(node):
        leaves.append(node)
        return
    for child in ast.iter_child_nodes(node):
        visit(child)

def label(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.arg):
        return node.arg
    if isinstance(node, ast.Attribute):
        return ast.unparse(node)
    return repr(node.value)

def place(node):
    if node in x:
        return [x[node]]
    xs = []
    for child in ast.iter_child_nodes(node):
        xs += place(child)
    if len(xs) > 0:
        x[node] = sum(xs) / len(xs)
    return xs

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
TOP = 200
BOTTOM = 120

def sx(node):
    return PAD + x[node] * GAP_X

def sy(node):
    return TOP + (top - y[node]) * GAP_Y

width = PAD * 2 + (len(leaves) - 1) * GAP_X
height = TOP + top * GAP_Y + BOTTOM
ground_y = sy(tree)

FONTS = "https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz@0,6..72;1,6..72&amp;family=Geist+Mono&amp;display=swap"

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append('<style>')
parts.append(f"@import url('{FONTS}');")
parts.append(".title { font: 52px Newsreader, Georgia, serif; fill: #ece7de; }")
parts.append(".doc { font: italic 21px Newsreader, Georgia, serif; fill: #8f8a80; }")
parts.append(".leaf { font: 17px 'Geist Mono', ui-monospace, monospace; text-anchor: middle; }")
parts.append(".ground { font: 13px 'Geist Mono', ui-monospace, monospace; fill: #8f8a80; letter-spacing: 0.04em; }")
parts.append('</style>')
parts.append(f'<rect width="{width}" height="{height}" fill="#0e0e0d"/>')

parts.append(f'<text class="title" x="{PAD}" y="96">{escape(name)}</text>')
parts.append(f'<text class="doc" x="{PAD}" y="134">{escape(summary)}</text>')

for node in x:
    for child in ast.iter_child_nodes(node):
        if child in x:
            w = 2 * math.sqrt(count(child))
            parts.append(f'<line x1="{sx(node)}" y1="{sy(node)}" x2="{sx(child)}" y2="{sy(child)}" stroke="#ece7de" stroke-width="{w}" stroke-linecap="round"/>')

for leaf in leaves:
    if isinstance(leaf, ast.Constant):
        colour = "#ece7de"
    else:
        colour = "#4fd08b"
    word = escape(str(label(leaf)))
    parts.append(f'<text class="leaf" x="{sx(leaf)}" y="{sy(leaf) - 16}" fill="{colour}">{word}</text>')

parts.append(f'<line x1="{PAD}" y1="{ground_y}" x2="{width - PAD}" y2="{ground_y}" stroke="#8f8a80" stroke-width="1"/>')
parts.append(f'<text class="ground" x="{PAD}" y="{ground_y + 40}">{escape(ground)}</text>')

parts.append('</svg>')

with open("poster.svg", "w") as f:
    f.write("\n".join(parts))
