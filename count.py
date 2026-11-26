import ast

code = "total = price * 2 + tax"
tree = ast.parse(code)

def count(node):
    if isinstance(node, ast.Name) or isinstance(node, ast.Constant):
        return 1
    num = 0
    for child in ast.iter_child_nodes(node):
        num += count(child)
    return num

    
print(count(tree))
