import ast

code = "total = price * 2 + tax"
tree = ast.parse(code)

def visit(node, depth):
    print("  " * depth + type(node).__name__, depth)

    for child in ast.iter_child_nodes(node):
        visit(child, depth + 1)

visit(tree, 0)
