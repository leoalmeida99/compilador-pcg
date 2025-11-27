import sys, traceback
sys.path.insert(0, r'c:\Users\lucas\Desktop\projeto compiladores')
from src.lexer import tokenize
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import Compiler
from src.vm import VM
from src.ast import *

print('=== Test Suite: mini-compilador ===')

# helper to print tokens
def show_tokens(code):
    print('\n--- Lexer test ---')
    print('Input:', repr(code))
    toks = list(tokenize(code))
    print('Tokens:')
    for t in toks:
        print(' ', t)
    return toks

# helper to pretty print AST
def ast_to_str(node, indent=0):
    pad = '  '*indent
    if isinstance(node, Program):
        s = pad + 'Program:\n'
        for st in node.statements:
            s += ast_to_str(st, indent+1)
        return s
    if isinstance(node, Number):
        return pad + f'Number({node.value})\n'
    if isinstance(node, Var):
        return pad + f'Var({node.name})\n'
    if isinstance(node, BinaryOp):
        return pad + f'BinaryOp({node.op})\n' + ast_to_str(node.left, indent+1) + ast_to_str(node.right, indent+1)
    if isinstance(node, Assign):
        return pad + f'Assign({node.name})\n' + ast_to_str(node.expr, indent+1)
    if isinstance(node, FunctionDef):
        return pad + f'FunctionDef({node.name}, params={node.params})\n' + ast_to_str(node.body, indent+1)
    if isinstance(node, Call):
        args = ''.join(ast_to_str(a, indent+1) for a in node.args)
        name = node.name if isinstance(node.name, str) else (node.name.name if isinstance(node.name, Var) else repr(node.name))
        return pad + f'Call({name})\n' + args
    return pad + f'<Unknown {type(node)}>\n'

# Test 1: Lexer
code1 = '1 + 2 * 3'
show_tokens(code1)

# Test 2: Parser precedence
print('\n--- Parser test (precedence) ---')
parser = Parser(code1 + '\n')
prog = parser.parse()
print(ast_to_str(prog))

# Test 3: Function parsing and assignment (example)
print('\n--- Parser test (functions and assignment) ---')
with open('examples/example.pcg','r',encoding='utf-8') as f:
    ex = f.read()
print('Source:\n', ex)
parser = Parser(ex)
prog = parser.parse()
print('AST:')
print(ast_to_str(prog))

# Test 4: Semantic analyzer success
print('\n--- Semantic test (should pass) ---')
sa = SemanticAnalyzer()
try:
    sa.analyze(prog)
    print('Semantic analysis: OK')
except Exception as e:
    print('Semantic analysis: FAILED ->', e)

# Test 5: Semantic analyzer failure (wrong arity)
print('\n--- Semantic test (wrong arity) ---')
bad_src = 'function f(x) = x + 1\nresult = f(1,2)\n'
print('Source:', bad_src)
parser = Parser(bad_src)
bad_prog = parser.parse()
sa2 = SemanticAnalyzer()
try:
    sa2.analyze(bad_prog)
    print('Semantic analysis (bad): unexpectedly passed')
except Exception as e:
    print('Semantic analysis (bad) correctly failed:')
    print(' ', type(e).__name__, str(e))

# Test 6: Codegen inspection
print('\n--- Codegen test (inspect bytecode) ---')
compiler = Compiler()
main, functions = compiler.compile(prog)
print('Main instructions:')
for i,ins in enumerate(main.instructions):
    print(' ', i, ins)
print('\nFunctions:')
for name, co in functions.items():
    print('Function', name, 'params=', co.params)
    for i,ins in enumerate(co.instructions):
        print('   ', i, ins)

# Test 7: VM execution
print('\n--- VM execution test ---')
vm = VM(main, functions)
res = vm.run()
print('VM run returned:', res)
print('Globals after run:')
for k,v in vm.globals.items():
    print(' ', k, '=', v)

# Test 8: VM runtime error (undefined var)
print('\n--- VM runtime error test (undefined var) ---')
src_err = 'x = y + 1\n'
print('Source:', src_err)
parser = Parser(src_err)
prog_err = parser.parse()
sa3 = SemanticAnalyzer()
try:
    sa3.analyze(prog_err)
    print('Semantic analysis: unexpectedly passed')
except Exception as e:
    print('Semantic error detected as expected:', e)

print('\n=== Test Suite Completed ===')
