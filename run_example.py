from src.lexer import tokenize
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import Compiler
from src.vm import VM

with open('examples/example.pcg', 'r', encoding='utf-8') as f:
    code = f.read()

print('Source:\n', code)

p = Parser(code)
program = p.parse()

sa = SemanticAnalyzer()
try:
    sa.analyze(program)
except Exception as e:
    print('Semantic error:', e)
    raise

compiler = Compiler()
main, functions = compiler.compile(program)

# The Compiler produced function codeobjects but without parameter name mapping.
# For now we will attach functions as produced in compiler.functions
vm = VM(main, functions)
res = vm.run()

print('Execution finished. Globals:')
for k,v in vm.globals.items():
    print(f'{k} = {v}')
