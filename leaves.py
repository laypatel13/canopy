import ast

code = "total = price * 2 + tax"
tree = ast.parse(code)

for node in ast.walk(tree):
    if isinstance(node, ast.Name):
        print(node.id)
    elif isinstance(node, ast.Constant):
        print(node.value)