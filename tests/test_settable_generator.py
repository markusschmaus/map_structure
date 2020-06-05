from map_structure.settable_generator import settable


def test_settable():
    def func(x):
        return 2 * x

    @settable
    def generator():
        result = []

        for x in range(3):
            y = yield(x)
            assert y == func(x)
            result.append(y)

        return result

    @settable
    def wrapper():
        result = yield from generator()
        assert result == [func(x) for x in range(3)]

    gen = wrapper()
    for x in gen:
        gen.set(func(x))
