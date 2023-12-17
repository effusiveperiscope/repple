# Repple
Quick and dirty opinionated fdisk-style REPLs
* Whitespace-separated command and arguments
* Except unary string functions
* Selector prompt
```python
from repple import Repple
r = Repple()
r['a'] = (lambda x: print(x+1), "Adds one to first argument and prints it")
r['A'] = lambda x: print(x+2)
def variadic_fn(*args):
  print(*[a+1 for a in args])

r.main()

```
```
Command: h
        q       Exits the program
        h       Show this help
        a       Adds one to first argument and prints it
        A
Command: a 1
2
Command: A 1
3
Command: b 1 2
2 3
```

## Selector
```python
from repple import Repple
r = Repple()
r['a'] = lambda: print(Repple.selector(['a','b','c']))
r.main()

```
```
Command: a
        1: a
        2: b
        3: c
Select your items: 1 3
['a', 'c']
```

## Unary string function
```python
from repple import Repple
r = Repple()
r.add_string_func('p', lambda x: print(x))
r.main()

```
```
Command: p Hello world!
Hello world!
```
