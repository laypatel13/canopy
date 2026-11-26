import ast

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

for node in x:
    print(type(node).__name__, x[node], y[node])