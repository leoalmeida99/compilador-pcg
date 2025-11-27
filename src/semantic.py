from .ast import *

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.functions = {}
        self.globals = {}

    def analyze(self, program: Program):
        # First pass: collect function signatures
        for stmt in program.statements:
            if isinstance(stmt, FunctionDef):
                if stmt.name in self.functions:
                    raise SemanticError(f"Function {stmt.name} already defined")
                self.functions[stmt.name] = len(stmt.params)
        # Second pass: validate bodies
        for stmt in program.statements:
            self.check_statement(stmt, local_params=None)
        return True

    def check_statement(self, stmt, local_params):
        if isinstance(stmt, FunctionDef):
            self.check_expression(stmt.body, local_params=stmt.params)
        elif isinstance(stmt, Assign):
            self.check_expression(stmt.expr, local_params=local_params)
            # assignment allowed to create globals
            self.globals[stmt.name] = True
        else:
            # expression
            self.check_expression(stmt, local_params=local_params)

    def check_expression(self, expr, local_params):
        if isinstance(expr, Number):
            return
        if isinstance(expr, Var):
            if local_params and expr.name in local_params:
                return
            if expr.name in self.globals:
                return
            if expr.name in self.functions:
                # referring to function as value is not allowed
                return
            raise SemanticError(f"Undefined variable {expr.name}")
        if isinstance(expr, BinaryOp):
            self.check_expression(expr.left, local_params)
            self.check_expression(expr.right, local_params)
            return
        if isinstance(expr, Call):
            # function name can be Var or nested expression; support Var only for now
            fname = expr.name if isinstance(expr.name, str) else (expr.name.name if isinstance(expr.name, Var) else None)
            if fname is None:
                # dynamic call unsupported
                raise SemanticError("Unsupported call expression")
            if fname not in self.functions:
                raise SemanticError(f"Call to undefined function {fname}")
            expected = self.functions[fname]
            if len(expr.args) != expected:
                raise SemanticError(f"Function {fname} expects {expected} args, got {len(expr.args)}")
            for a in expr.args:
                self.check_expression(a, local_params)
            return
        raise SemanticError(f"Unsupported expression type: {type(expr)}")
