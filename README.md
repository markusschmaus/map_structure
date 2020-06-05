# map_structure
Use python generators to create a copy of some structured container with it's values modified

Guido van van Rossum, the author of Python, famously isn't very fond of `lambda` expressions and the functional constructs like `map` or `filter` which use them. He even [suggested removing them altogether](https://www.artima.com/weblogs/viewpost.jsp?thread=98196), pointing out that a list comprehension is a more pythonic alternative: 
```python
[f(x) for x in old_list if cond(x)]
```

I agree that this is a perfect replacement for lists, but besides besides list comprehensions, Python only has set and dict comprehensions, and they don't exist for custom containers.

One option would be to add a custom `map` method to your custom container, which again would require the loathed `lambda` expression.

Alternatively, if the constructor of your custom container accepts an `Iterable` you can use a generator expression to achieve something which looks like a custom container comprehension.

```python
CustomContainer(
    f(x) 
    for x in custom_container 
    if cond(x)
)
``` 

But not every container can be easily unpacked into an iterable and even fewer can be constructed from an unstructured sequence of values.

This package combines these two options by providing a `map` function which uses an iterator rather than a `lambda` expression.

```python
container.map(f(x) for x in container if cond(x))
``` 

It also provides this functionality for nested builtin contains.

```python
structure = map_structure(
    {'a': 1, 'b': [[2, 3], 4], 'c': 2, 'd': 5}
)

structure.map(
    2 * x
    for x in structure  
    if x != 2
)
```

returns `{'a': 2, 'b': [[6], 8], 'd': 10}`

## Settable generators

[PEP 342](https://www.python.org/dev/peps/pep-0342/) introduced the ability to send data back to the a generator. However since [the extended continue statement](https://www.python.org/dev/peps/pep-0342/#the-extended-continue-statement) was dropped from the proposal, they [cannot be used in a for loop](https://stackoverflow.com/questions/36835782/using-generator-send-within-a-for-loop).

So instead of
```python
for n in generator():
  continue process(n)
```

we would need to write

```python
gen = generator()
try:
  n = next(gen)
  while True:
    n = gen.send(process(n))
except StopIteration:
    pass
```

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
