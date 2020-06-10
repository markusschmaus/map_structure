import pytest  # type: ignore

from settable_generator.settable_generator import settable


@pytest.fixture()
def func():
    def inner(x):
        return 2 * x

    return inner


@pytest.fixture()
def generator(func):
    def inner():
        result = []

        for x in range(3):
            y = yield (x)
            result.append(y)

        return result

    return inner


@pytest.fixture()
def settable_generator(generator):
    return settable(generator)


def test_settable_with_default(generator):
    @settable(default='default')
    def settable_generator():
        result = yield from generator()
        return result

    gen = settable_generator()
    for x in gen:
        pass

    assert gen.result == ['default' for x in range(3)]


def test_settable_bare(generator):
    @settable
    def settable_generator():
        result = yield from generator()
        return result

    gen = settable_generator()
    for x in gen:
        pass

    assert gen.result == [None for x in range(3)]


def test_settable_map(func, settable_generator):
    gen = settable_generator()
    result = gen.map(func(x) for x in gen)
    assert result == [func(x) for x in range(3)]


def test_settable_for_loop(func, settable_generator):
    gen = settable_generator()
    for x in gen:
        gen.set(func(x))

    assert gen.result == [func(x) for x in range(3)]


def test_settable_yield_from(func, settable_generator):
    @settable()
    def wrapper():
        result = yield from settable_generator()
        assert result == [func(x) for x in range(3)]

    gen = wrapper()
    for x in gen:
        gen.set(func(x))


def test_assignment_expression(func, settable_generator):
    for x in (gen := settable_generator()):
        gen.set(func(x))
    result = gen.result
    assert result == [func(x) for x in range(3)]


def test_method(generator):
    class C:
        def __init__(self):
            self.accumulator = []

        @settable
        def generator(self):
            for x in generator():
                res = yield x
                self.accumulator.append(res)
            return self.accumulator

    c = C()

    for x in (g := c.generator()):
        g.set(x)

    assert c.accumulator == list(range(3))

    for x in (g := c.generator()):
        g.set(3 + x)

    assert c.accumulator == list(range(6))
