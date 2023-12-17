import inspect
import sys
import ast
from itertools import count, islice
from enum import Enum

class Repple_BreakException(Exception): pass
class Repple_ContinueException(Exception): pass
class Repple_NotUnaryException(Exception): pass

class KeyMap:
    Integers = 1
    QwertyWithCaps = ("1234567890qwertyuiopasdfghjklzxcvbnm"
         "!@#$%^&*()QWERTYUIOPASDFGHJKLZXCVBNM")

class Repple:
    @staticmethod
    def selector(items, # Accepts either a list or a dict. Dict keys are labels
        keymap = KeyMap.Integers,
        select_str = "Select your items: ",
        validator = None,
        is_unary = False):
        
        labels = None

        if type(items) == dict:
            labels = list(items.keys())
            items = list(items.values())

        if keymap != KeyMap.Integers and (len(items) > len(keymap)):
            print(f"--Number of items exceeds keymap length, "
                  f"fallback to integers")
            keymap = KeyMap.Integers
        if keymap == KeyMap.Integers:
            keymap = count(start=1)
        mapped_keys = list(islice(keymap, len(items)))
        items_map = {}
        labels_map = {}
        for i,v in enumerate(items):
            items_map[str(mapped_keys[i])] = v
            if labels is not None:
                labels_map[str(mapped_keys[i])] = labels[i]
            else:
                labels_map[str(mapped_keys[i])] = v

        while True:
            try:
                for k,v in labels_map.items():
                    print(f"\t{k}: {v}")
                line = input(select_str)
                args = line.split()
                ret = []
                if is_unary and len(args) > 1:
                    print("--Only one argument expected")
                    continue
                for a in args:
                    if not a in items_map:
                        raise Repple_ContinueException
                    ret.append(items_map[a])
            except Repple_ContinueException:
                continue
            return ret

    def __init__(self):
        self.command_map = {}
        self['q'] = (lambda: exec('raise Repple_BreakException'),
                     "Exits the program")
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

        min_params = fn_param_count
        if variadic_positional:
            min_params -= 1

        self.command_map[index] = {
            "func": func,
            "nullary": fn_param_count == 0,
            "params": [p for p in signature.parameters],
            "param_count": fn_param_count,
            "min_params": min_params,
            "variadic": variadic_positional,
            "desc": desc,
            "accept_str": False}
        return index

    # Add a unary function that accepts an arbitrary string (including whitespace)
    def add_string_func(self, index : str, value, desc : str = ""):
        self[index] = (value, desc)
        assert self.command_map[index]['param_count'] == 1
        # Just toggles a flag; handling is in main()
        self.command_map[index]['accept_str'] = True

    def default_help(self):
        for k,v in self.command_map.items():
            paramstring = ' '.join([f'<{param}>' for param in v['params']])
            print(f'\t{k+" "+paramstring:<20} {v["desc"]:>5}')

    def remove(self, index : str):
        self.command_map.remove(index)

    def desc(self, key):
        if key in self.command_map:
            if len(self.command_map[key]["desc"]):
                return self.command_map[key]["desc"]+f" ({key})"
            return key+f"({self.command_map[key]['func']})"
        else:
            return None

    def arg_eval(self, x):
        try:
            return ast.literal_eval(x)
        except (SyntaxError,ValueError):
            return x

    def main(self, **kwargs):
        command_str = kwargs.get('command_str') or "Command: "
        while True:
            try:
                line = input(command_str)
                if not len(line):
                    continue
                split = line.split()
                cmd = split[0]
                args = [self.arg_eval(x) for x in split[1:]]
                if cmd in self.command_map:
                    nullary = self.command_map[cmd]['nullary']
                    if nullary:
                        self.command_map[cmd]['func']()
                    elif self.command_map[cmd]['accept_str']:
                        residual_str = line[len(cmd):].strip()
                        self.command_map[cmd]['func'](residual_str)
                    else:
                        exp_param_count = self.command_map[cmd]['param_count']
                        min_params = self.command_map[cmd]['min_params']
                        max_params = exp_param_count
                        is_variadic = self.command_map[cmd]['variadic']
                        disp_params = (exp_param_count if not is_variadic else
                            min_params)
                        if (len(args) < min_params) or (
                            len(args) > max_params and not is_variadic):
                            print(f"--Command {self.desc(cmd)} expects "
                                  f"{disp_params} params")
                            continue
                        self.command_map[cmd]['func'](*args)
                elif len(cmd):
                    print(f"--No command {cmd} found")
            except Repple_BreakException:
                return
