class Node:
    pass

class Number(Node):
    def __init__(self, value):
        self.value = value

class Var(Node):
    def __init__(self, name):
        self.name = name

class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class FunctionDef(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Call(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Program(Node):
    def __init__(self, statements):
        self.statements = statements
