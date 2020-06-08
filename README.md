# settable_generator
Allow python generators to receive values in for loops.

Python's support for functional constructs is a mixed bag. While functions are a first class objects, it's support for anonymous functions is very limited. 

A common argument you hear is that [anonymous functions are overused anyway](https://treyhunner.com/2018/09/stop-writing-lambda-expressions/) and that it's better to use named functions instead. That this argument is flawed becomes obvious when looking at two other constructs that allow for anonymous code blocks in Python. [PEP 343](https://www.python.org/dev/peps/pep-0343) introduced `with` blocks which allow the programmer to anonymously define a block of code which is then executed within the context provided by a context manager. And even more importantly `for` loops allows the programmer to anonymously define a code block which is then executed for every value provided by the iterator. Imagine how much less clear your Python code would be if you had to use named functions in this instances instead.

```python
def do_stuff(x):
    ...

for range(10): do_stuff
```

```python
def do_stuff(f):
    ...

File.open(do_stuff)
```

While these two constructs cover the large range of use cases for anonymous code blocks, they suffer from the limitation that they are one way. While the `for` loop can invoke the anonymous block associated for it for an arbitrary number times with arbitrary values, it cannot receive any results from the invoked function.

Ironically around the same time the `with` block was introduced, [PEP 342](https://www.python.org/dev/peps/pep-0342/) enhanced generators to be able to receive values, but the proposal to make this accessible from inside a `for` using the [extended `continue` statement](https://www.python.org/dev/peps/pep-0342/#the-extended-continue-statement) was rejected. 

One instance where the ability to send back data would be very usefull is [when working with graphs](https://stackoverflow.com/questions/36835782/using-generator-send-within-a-for-loop).

## Setable generator

It's impossible to implement the extended `continue` in a Python package. However a similar result can be achieved by using a settable generator.

```python
@setable
def generator():
    ...
    send_value = yield yield_value
    ...

gen = generator()
for n in gen:
    gen.set(process(n))
```

the value passed to the `set` method of a setable generator is stored and sent to the generator the next time `__next__` is invoked.

## Examples

Map values in a complex container class like a tree to some new values.

```python
class Tree:
    def __init__(self, value, children):
        self.value = value
        self.children = children

    @settable
    def replace_values(self):
        new_children = []
        for child in self.children:
            new_child = yield from child.replace_values()
            new_children.append(new_child)
        
        new_value = yield self.value
        return Tree(new_value, new_children)

tree = Tree(...)

for old_value in replace := tree.replace_values():
    replace.set(old_value * 2) 
```
