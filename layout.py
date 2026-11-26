import ast

code = "total = price * 2 + tax"
tree = ast.parse(code)

leaves = []
x = {}

def visit(node):
    if isinstance(node, ast.Name) or isinstance(node, ast.Constant):
        leaves.append(node)
    for child in ast.iter_child_nodes(node):
        visit(child)

def label(node):
    if isinstance(node, ast.Name):
        return node.id
    return node.value

visit(tree)

for i, leaf in enumerate(leaves):
    x[leaf] = i

for leaf in leaves:
    print(label(leaf), x[leaf])