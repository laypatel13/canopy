import ast
code = "total = price * (2 + tax)"
tree = ast.parse(code)
print(ast.dump(tree, indent=4))
