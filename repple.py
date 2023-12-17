import inspect
import sys
import ast

class Repple:
    def __init__(self):
        self.command_map = {}
        self['q'] = (lambda: sys.exit(), "Exits the program")
        self['h'] = (self.default_help, "Show this help")

    def __setitem__(self, index : str, value):
        assert(type(index) == str)

        if isinstance(value, tuple): # Accept a tuple with a function and desc
            func = value[0]
            desc = value[1]
        else: # Or just a function
            func = value
            desc = ""
        assert(callable(func))
        signature = inspect.signature(func)
        fn_param_count = len(signature.parameters)

        # kwargs considered out of scope
        variadic_positional = any(
            p.kind == inspect.Parameter.VAR_POSITIONAL for p in
            signature.parameters.values())

        self.command_map[index] = {
            "func": func,
            "nullary": fn_param_count == 0,
            "param_count": fn_param_count,
            "variadic": variadic_positional,
            "desc": desc}
        return index

    def default_help(self):
        for k,v in self.command_map.items():
            print(f'\t{k}\t{v["desc"]}')

    def remove(self, index : str):
        self.command_map.remove(index)

    def desc(self, key):
        if key in self.command_map:
            if len(self.command_map[key]["desc"]):
                return self.command_map[key]["desc"]+f" ({key})"
            return key+f"({self.command_map[key]['func']})"
        else:
            return None

    def main(self, **kwargs):
        command_str = kwargs.get('command_str') or "Command: "
        while True:
            line = input(command_str)
            if not len(line):
                continue
            split = line.split()
            cmd = split[0]
            args = [ast.literal_eval(x) for x in split[1:]]
            if cmd in self.command_map:
                nullary = self.command_map[cmd]['nullary']
                if nullary:
                    self.command_map[cmd]['func']()
                else:
                    exp_param_count = self.command_map[cmd]['param_count']
                    is_variadic = self.command_map[cmd]['variadic']
                    if (exp_param_count != len(args)) and not is_variadic:
                        print(f"--Command {self.desc(cmd)} expects "
                              f"{exp_param_count} params")
                        continue
                    self.command_map[cmd]['func'](*args)
            elif len(cmd):
                print(f"--No command {cmd} found")
