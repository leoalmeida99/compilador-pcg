from .ast import *

# Simple bytecode instructions
# PUSH_CONST idx
# LOAD_VAR name
# STORE_VAR name
# CALL name, argc
# RET
# ADD, SUB, MUL, DIV, POW

class CodeObject:
    def __init__(self, instructions, consts, params=None):
        self.instructions = instructions
        self.consts = consts
        self.params = params or []

class Compiler:
    def __init__(self):
        self.consts = []
        self.instructions = []
        self.functions = {}
        self.current_params = None

    def compile(self, program: Program):
        # compile function bodies first to code objects
        for stmt in program.statements:
            if isinstance(stmt, FunctionDef):
                co = self.compile_function(stmt)
                self.functions[stmt.name] = co
        # compile top-level statements into a main code object
        self.consts = []
        self.instructions = []
        for stmt in program.statements:
            if not isinstance(stmt, FunctionDef):
                self.emit_statement(stmt)
        self.instructions.append(('RET',))
        main = CodeObject(self.instructions, self.consts)
        return main, self.functions

    def compile_function(self, fdef: FunctionDef):
        c = Compiler()
        c.current_params = list(fdef.params)
        c.consts = []
        c.instructions = []
        c.emit_expression(fdef.body)
        c.instructions.append(('RET',))
        return CodeObject(c.instructions, c.consts, params=list(fdef.params))

    def emit_statement(self, stmt):
        if isinstance(stmt, Assign):
            self.emit_expression(stmt.expr)
            self.instructions.append(('STORE_VAR', stmt.name))
            return
        else:
            # expression statement: evaluate and drop
            self.emit_expression(stmt)
            self.instructions.append(('POP',))

    def emit_expression(self, expr):
        if isinstance(expr, Number):
            idx = self._add_const(expr.value)
            self.instructions.append(('PUSH_CONST', idx))
            return
        if isinstance(expr, Var):
            # if inside a function and var is a parameter, load local
            if self.current_params and expr.name in self.current_params:
                self.instructions.append(('LOAD_LOCAL', expr.name))
            else:
                self.instructions.append(('LOAD_VAR', expr.name))
            return
        if isinstance(expr, BinaryOp):
            self.emit_expression(expr.left)
            self.emit_expression(expr.right)
            op = expr.op
            if op == '+': self.instructions.append(('ADD',))
            elif op == '-': self.instructions.append(('SUB',))
            elif op == '*': self.instructions.append(('MUL',))
            elif op == '/': self.instructions.append(('DIV',))
            elif op == '^': self.instructions.append(('POW',))
            else:
                raise Exception('Unknown op '+op)
            return
        if isinstance(expr, Call):
            # evaluate args
            for a in expr.args:
                self.emit_expression(a)
            # push call
            fname = expr.name if isinstance(expr.name, str) else (expr.name.name if isinstance(expr.name, Var) else None)
            if fname is None:
                raise Exception('Unsupported call target')
            self.instructions.append(('CALL', fname, len(expr.args)))
            return
        raise Exception('Unsupported expr in codegen: '+str(type(expr)))

    def _add_const(self, v):
        try:
            return self.consts.index(v)
        except ValueError:
            self.consts.append(v)
            return len(self.consts)-1
