import ast

code = "total = price * 2 + tax"
tree = ast.parse(code)

def visit(node):
        if isinstance(node, ast.Name):
            print(node.id)
        elif isinstance(node, ast.Constant):
            print(node.value)

        for child in ast.iter_child_nodes(node):
            visit(child)


visit(tree)
