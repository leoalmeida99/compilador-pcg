import math

class Frame:
    def __init__(self, codeobj, globals_, functions):
        self.code = codeobj
        self.ip = 0
        self.stack = []
        self.locals = {}
        self.globals = globals_
        self.functions = functions

class VMError(Exception):
    pass

class VM:
    def __init__(self, main_code, functions):
        self.main = main_code
        self.functions = functions
        self.globals = {}

    def run(self):
        frame = Frame(self.main, self.globals, self.functions)
        return self.run_frame(frame)

    def run_frame(self, frame: Frame):
        instrs = frame.code.instructions
        consts = frame.code.consts
        stack = frame.stack
        while frame.ip < len(instrs):
            ins = instrs[frame.ip]
            frame.ip += 1
            op = ins[0]
            if op == 'PUSH_CONST':
                idx = ins[1]
                stack.append(consts[idx])
            elif op == 'LOAD_VAR':
                name = ins[1]
                if name in frame.locals:
                    stack.append(frame.locals[name])
                elif name in frame.globals:
                    stack.append(frame.globals[name])
                else:
                    raise VMError(f'Undefined variable {name}')
            elif op == 'STORE_VAR':
                name = ins[1]
                val = stack.pop()
                frame.globals[name] = val
            elif op == 'LOAD_LOCAL':
                name = ins[1]
                if name in frame.locals:
                    stack.append(frame.locals[name])
                else:
                    raise VMError(f'Undefined local {name}')
            elif op == 'POP':
                stack.pop()
            elif op == 'ADD':
                b = stack.pop(); a = stack.pop(); stack.append(a+b)
            elif op == 'SUB':
                b = stack.pop(); a = stack.pop(); stack.append(a-b)
            elif op == 'MUL':
                b = stack.pop(); a = stack.pop(); stack.append(a*b)
            elif op == 'DIV':
                b = stack.pop(); a = stack.pop(); stack.append(a/b)
            elif op == 'POW':
                b = stack.pop(); a = stack.pop(); stack.append(math.pow(a,b))
            elif op == 'CALL':
                fname = ins[1]; argc = ins[2]
                args = [stack.pop() for _ in range(argc)][::-1]
                if fname not in self.functions:
                    raise VMError(f'Call to undefined function {fname}')
                co = self.functions[fname]
                # create new frame for function
                fframe = Frame(co, frame.globals, self.functions)
                # bind params by name if available
                for i, a in enumerate(args):
                    if i < len(co.params):
                        pname = co.params[i]
                        fframe.locals[pname] = a
                    else:
                        fframe.locals[f'arg{i}'] = a
                # Execute function: because compiler uses variable names of parameters, we need to map names accordingly.
                # For simplicity, we will set locals with parameter names expected by function if available.
                # But our Compiler currently doesn't store param names in CodeObject; to keep simple, assume function bodies use arg0..argN
                res = self.run_frame(fframe)
                stack.append(res)
            elif op == 'RET':
                # return top of stack or None
                return stack.pop() if stack else None
            else:
                raise VMError('Unknown instruction '+op)
        return None
