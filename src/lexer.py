import re

TOKEN_SPEC = [
    ('NUMBER',   r'\d+(?:\.\d+)?'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('ASSIGN',   r'='),
    ('COMMA',    r','),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('OP',       r'[+\-*/^]'),
    ('SKIP',     r'[ \t]+'),
    ('NEWLINE',  r'\n'),
    ('MISMATCH', r'.'),
]

MASTER_RE = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))
KEYWORDS = {'function'}

class Token:
    def __init__(self, type_, value, pos):
        self.type = type_
        self.value = value
        self.pos = pos
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


def tokenize(code):
    pos = 0
    line = 1
    for mo in MASTER_RE.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
            yield Token('NUMBER', value, pos)
        elif kind == 'ID':
            if value in KEYWORDS:
                yield Token(value.upper(), value, pos)
            else:
                yield Token('ID', value, pos)
        elif kind == 'OP':
            yield Token('OP', value, pos)
        elif kind in ('ASSIGN','COMMA','LPAREN','RPAREN'):
            yield Token(kind, value, pos)
        elif kind == 'NEWLINE':
            yield Token('NEWLINE', '\n', pos)
        elif kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected char {value!r} at pos {pos}')
        pos = mo.end()
    yield Token('EOF', '', pos)
