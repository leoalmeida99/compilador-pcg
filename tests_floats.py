import sys
sys.path.insert(0, r'c:\Users\lucas\Desktop\projeto compiladores')
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import Compiler
from src.vm import VM

print('=== Float Tests ===')

cases = [
    ("result = 1.5 + 2.25 * 2\n", 'result', 6.0),
    ("result = 5 / 2\n", 'result', 2.5),
    ("result = 2 ^ 3\n", 'result', 8.0),
    ("result = 9 ^ 0.5\n", 'result', 3.0),
    ("result = 1 + 2.5\n", 'result', 3.5),
    ("result = 1 + 2 * 3.0\n", 'result', 7.0),
    ("result = 1 / 2\n", 'result', 0.5),
]

EPS = 1e-9

for i, (src, name, expected) in enumerate(cases, 1):
    print(f'\nTest {i}:', src.strip())
    try:
        p = Parser(src)
        prog = p.parse()
        sa = SemanticAnalyzer()
        sa.analyze(prog)
        compiler = Compiler()
        main, functions = compiler.compile(prog)
        vm = VM(main, functions)
        vm.run()
        if name not in vm.globals:
            print('  FAIL: variable', name, 'not set')
            continue
        val = vm.globals[name]
        ok = False
        try:
            # compare floats approximately
            ok = abs(float(val) - float(expected)) < EPS
        except Exception:
            ok = (val == expected)
        if ok:
            print('  PASS ->', name, '=', val)
        else:
            print('  FAIL ->', name, '=', val, 'expected', expected)
    except Exception as e:
        print('  ERROR during test:', type(e).__name__, e)

print('\n=== Float Tests Completed ===')
