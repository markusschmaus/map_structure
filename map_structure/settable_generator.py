from functools import wraps
from types import TracebackType
from typing import TypeVar, Generator, Type, Optional


_T_co = TypeVar('_T_co', covariant=True)
_V_co = TypeVar('_V_co', covariant=True)
_T_contra = TypeVar('_T_contra', contravariant=True)


class SettableGenerator(Generator[_T_co, _T_contra, _V_co]):
    generator: Generator[_T_co, _T_contra, _V_co]
    send_value: Optional[_T_contra]
    is_set: bool

    def __init__(self, generator: Generator[_T_co, _T_contra, _V_co]):
        self.generator = generator
        self.send_value = None
        self.is_set = False

    def set(self, value:_T_contra):
        if self.is_set:
            raise RuntimeError(
                'Generator has already been set to {}'.format(self.send_value))
        self.send_value = value
        self.is_set = True

    def __next__(self) -> _T_co:
        if self.is_set:
            send_value = self.send_value
            self.is_set = False
            self.send_value = None
            return self.generator.send(send_value)
        else:
            return self.generator.__next__()

    def send(self, value: _T_contra) -> _T_co:
        if self.is_set:
            raise RuntimeError(
                'Generator has already been set to {}'.format(self.send_value))
        return self.generator.send(value)

    def throw(self, typ: Type[BaseException],
              val: Optional[BaseException] = None,
              tb: Optional[TracebackType] = None) -> _T_co:
        return self.generator.throw(typ, val, tb)


def settable(iterator):
    @wraps(iterator)
    def inner(*args, **kwargs):
        return SettableGenerator(iterator(*args, **kwargs))

    return inner
