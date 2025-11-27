from .lexer import tokenize, Token
from .ast import *

class Parser:
    def __init__(self, code):
        self.tokens = list(tokenize(code))
        self.pos = 0
        self.current = self.tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        return self.current

    def accept(self, ttype):
        if self.current.type == ttype:
            val = self.current.value
            self.advance()
            return val
        return None

    def expect(self, ttype):
        if self.current.type == ttype:
            val = self.current.value
            self.advance()
            return val
        raise SyntaxError(f'Expected {ttype} at pos {self.current.pos}, got {self.current.type}')

    def parse(self):
        stmts = []
        while self.current.type != 'EOF':
            if self.current.type == 'NEWLINE':
                self.advance(); continue
            stmts.append(self.parse_statement())
        return Program(stmts)

    def parse_statement(self):
        if self.current.type == 'FUNCTION':
            return self.parse_function_def()
        elif self.current.type == 'ID':
            # could be assignment or expression
            # lookahead
            if self.tokens[self.pos+1].type == 'ASSIGN':
                name = self.expect('ID')
                self.expect('ASSIGN')
                expr = self.parse_expression()
                # optional newline
                if self.current.type == 'NEWLINE':
                    self.advance()
                return Assign(name, expr)
            else:
                expr = self.parse_expression()
                if self.current.type == 'NEWLINE':
                    self.advance()
                return expr
        else:
            expr = self.parse_expression()
            if self.current.type == 'NEWLINE':
                self.advance()
            return expr

    def parse_function_def(self):
        self.expect('FUNCTION')
        name = self.expect('ID')
        self.expect('LPAREN')
        params = []
        if self.current.type == 'ID':
            params.append(self.expect('ID'))
            while self.current.type == 'COMMA':
                self.advance()
                params.append(self.expect('ID'))
        self.expect('RPAREN')
        self.expect('ASSIGN')
        body = self.parse_expression()
        if self.current.type == 'NEWLINE':
            self.advance()
        return FunctionDef(name, params, body)

    # Expression grammar: parse lowest precedence first via recursive descent
    def parse_expression(self):
        return self.parse_add_sub()

    def parse_add_sub(self):
        node = self.parse_mul_div()
        while self.current.type == 'OP' and self.current.value in ('+','-'):
            op = self.current.value
            self.advance()
            right = self.parse_mul_div()
            node = BinaryOp(op, node, right)
        return node

    def parse_mul_div(self):
        node = self.parse_power()
        while self.current.type == 'OP' and self.current.value in ('*','/'):
            op = self.current.value
            self.advance()
            right = self.parse_power()
            node = BinaryOp(op, node, right)
        return node

    def parse_power(self):
        node = self.parse_call_primary()
        while self.current.type == 'OP' and self.current.value == '^':
            op = self.current.value
            self.advance()
            right = self.parse_call_primary()
            node = BinaryOp(op, node, right)
        return node

    def parse_call_primary(self):
        node = self.parse_primary()
        # function call
        while self.current.type == 'LPAREN':
            self.advance()
            args = []
            if self.current.type != 'RPAREN':
                args.append(self.parse_expression())
                while self.current.type == 'COMMA':
                    self.advance()
                    args.append(self.parse_expression())
            self.expect('RPAREN')
            node = Call(node.name if isinstance(node, Var) else node, args)
        return node

    def parse_primary(self):
        if self.current.type == 'NUMBER':
            val = self.current.value
            self.advance()
            return Number(val)
        if self.current.type == 'ID':
            name = self.current.value
            self.advance()
            return Var(name)
        if self.current.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f'Unexpected token {self.current}')
