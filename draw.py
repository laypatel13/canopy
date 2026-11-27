import ast
from html import escape
from datetime import date  
import inspect, shlex
import math
import os
import platform
import re
import sys

number = sys.argv[1]
code = sys.stdin.read()
tree = ast.parse(code)

def find_function(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node

func = find_function(tree)
tree.body = [func]
func.returns = None

kept = []

for arg in func.args.args:
    if arg.arg != "self":
        kept.append(arg)

func.args.args = kept

doc = ast.get_docstring(func)
summary = ""

if doc is not None:
    func.body = func.body[1:]
    summary = doc.splitlines()[0]

name = func.name
ground = f"LeetCode {number} · {date.today()}"

leaves = []
x = {}
y = {}

SYMBOLS = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//",
    ast.Mod: "%", ast.Pow: "**", ast.LShift: "<<", ast.RShift: ">>",
    ast.BitOr: "|", ast.BitXor: "^", ast.BitAnd: "&", ast.MatMult: "@",
    ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
    ast.Is: "is", ast.IsNot: "is not", ast.In: "in", ast.NotIn: "not in",
    ast.And: "and", ast.Or: "or", ast.Not: "not", ast.USub: "-", ast.UAdd: "+", ast.Invert: "~",
}

JOINTS = {
    ast.arguments: "args",
    ast.Return: "return",
    ast.For: "for",
    ast.While: "while",
    ast.If: "if",
}

def is_leaf(node):
    return isinstance(node, (ast.Name, ast.Constant, ast.arg, ast.Attribute, ast.operator, ast.cmpop, ast.boolop, ast.unaryop))  

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
    if type(node) in SYMBOLS:
        return SYMBOLS[type(node)]
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

for node in ast.walk(tree):
    if hasattr(node, "op"):
        node.op = type(node.op)()
    if isinstance(node, ast.Compare):
        fresh = []
        for op in node.ops:
            fresh.append(type(op)())
        node.ops = fresh

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

W = 1200
H = round(W * 2 ** 0.5)
PAD = 100
BOTTOM = 170
LEAF_SIZE = 18

words = [str(label(leaf)) for leaf in leaves]
longest = max(len(word) for word in words) * LEAF_SIZE * 0.6
TOP = 300 + longest
ground_y = H - BOTTOM
GAP_X = (W - PAD * 2) / max(len(leaves) - 1, 1)
GAP_Y = (ground_y - TOP) / top

def sx(node):
    return PAD + x[node] * GAP_X

def sy(node):
    return TOP + (top - y[node]) * GAP_Y

FONTS = "https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz@0,6..72;1,6..72&amp;family=Geist+Mono&amp;display=swap"

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append('<style>')
parts.append(f"@import url('{FONTS}');")
parts.append(".title { font: 76px Newsreader, Georgia, serif; fill: #ece7de; }")
parts.append(".doc { font: 26px Newsreader, Georgia, serif; fill: #8f8a80; }")
parts.append(f".leaf {{ font: {LEAF_SIZE}px 'Geist Mono', ui-monospace, monospace; dominant-baseline: central; }}")
parts.append(".ground { font: 15px 'Geist Mono', ui-monospace, monospace; fill: #8f8a80; letter-spacing: 0.04em; }")
parts.append(".joint { font: 14px 'Geist Mono', ui-monospace, monospace; fill: #8f8a80; dominant-baseline: central; paint-order: stroke; stroke: #0e0e0d; stroke-width: 6px; stroke-linejoin: round; }")
parts.append('</style>')
parts.append(f'<rect width="{W}" height="{H}" fill="#0e0e0d"/>')

parts.append(f'<text class="title" x="{PAD}" y="170">{escape(name)}</text>')
caption = re.sub(r"\*([^*\s][^*]*?)\*", r'<tspan font-style="italic">\1</tspan>', escape(summary))
parts.append(f'<text class="doc" x="{PAD}" y="218">{caption}</text>')

for node in x:
    for child in ast.iter_child_nodes(node):
        if child in x:
            w = round(2 * math.sqrt(count(child)), 1)
            x1, y1 = sx(node), sy(node)
            x2, y2 = sx(child), sy(child)
            mid = (y1 + y2) / 2
            cap = "butt" if node is tree else "round"
            parts.append(f'<path d="M {x1} {y1} C {x1} {mid}, {x2} {mid}, {x2} {y2}" fill="none" stroke="#ece7de" stroke-width="{w}" stroke-linecap="{cap}"/>')

for node in x:
    if type(node) in JOINTS:
        jx, jy = sx(node), sy(node)
        parts.append(f'<circle cx="{jx}" cy="{jy}" r="4" fill="#0e0e0d" stroke="#ece7de" stroke-width="1.5"/>')
        parts.append(f'<text class="joint" x="{jx + 12}" y="{jy}">{JOINTS[type(node)]}</text>')

for leaf in leaves:
    if type(leaf) in SYMBOLS:
        colour = "#8f8a80"
    elif isinstance(leaf, ast.Constant):
        colour = "#ece7de"
    else:
        colour = "#4fd08b"
    word = escape(str(label(leaf)))
    lx, ly = sx(leaf), sy(leaf) - 16
    parts.append(f'<text class="leaf" x="{lx}" y="{ly}" fill="{colour}" transform="rotate(-90 {lx} {ly})">{word}</text>')

parts.append(f'<line x1="{PAD}" y1="{ground_y}" x2="{W - PAD}" y2="{ground_y}" stroke="#8f8a80" stroke-width="1"/>')
parts.append(f'<text class="ground" x="{PAD}" y="{ground_y + 50}">{escape(ground)}</text>')

parts.append('</svg>')

with open(f"{number}.py", "w") as f:
    f.write(code)

with open(f"{number}.svg", "w") as f:
    f.write("\n".join(parts))
