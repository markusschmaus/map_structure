from functools import wraps, partial
from types import TracebackType
from typing import TypeVar, Generator, Type, Optional, Any, overload, \
    Callable, Generic, Union


_T_co = TypeVar('_T_co', covariant=True)
_V_co = TypeVar('_V_co', covariant=True)
_T_cntr = TypeVar('_T_cntr', contravariant=True)
_T = TypeVar('_T')


class UnsetType:
    def __repr__(self):
        return "Unset"


Unset = UnsetType()

MaybeUnset = Union[UnsetType, _T]


class SettableGenerator(Generator[_T_co, _T_cntr, _V_co]):
    generator: Generator[_T_co, _T_cntr, _V_co]
    _result: _V_co
    default: MaybeUnset[_T_cntr]
    _send_value: MaybeUnset[_T_cntr]
    _initialized: bool
    _exhausted: bool

    def __init__(
            self,
            generator: Generator[_T_co, _T_cntr, _V_co],
            default: MaybeUnset[_T_cntr] = Unset
    ):
        self.generator = generator
        self.default = default
        self._send_value = Unset
        self._exhausted = False
        self._initialized = False

    def set(self, value: _T_cntr):
        if not self._initialized:
            raise RuntimeError('Generator first needs to be initilized by '
                               'calling next')
        self._ensure_not_set()
        self._send_value = value

    def __next__(self) -> _T_co:
        if self._initialized:
            send_value: _T_cntr
            if not isinstance(self._send_value, UnsetType):
                send_value = self._send_value
            else:
                if isinstance(self.default, UnsetType):
                    raise RuntimeError('Generator not set and no default provided')
                else:
                    send_value = self.default
            self._send_value = Unset
            return self.forward(send_value)
        else:
            self._initialized = True
            try:
                return self.generator.__next__()
            except StopIteration as e:
                self._exhausted = True
                self._result = e.value
                raise e

    def send(self, send_value: _T_cntr) -> _T_co:
        self._ensure_not_set()
        return self.forward(send_value)

    @property
    def is_set(self) -> bool:
        return not isinstance(self._send_value, UnsetType)

    def __iter__(self):
        return self

    def close(self):
        return super().close()

    def _ensure_not_set(self):
        if self.is_set:
            raise RuntimeError(
                'Generator has already been set to {}'.format(
                    self._send_value))

    def forward(self, send_value: _T_cntr) -> _T_co:
        try:
            return self.generator.send(send_value)
        except StopIteration as e:
            self._exhausted = True
            self._result = e.value
            raise e

    @property
    def result(self) -> _V_co:
        if not self._exhausted:
            raise RuntimeError(
                'Result not available for incomplete generators')
        return self._result

    def throw(self, typ: Type[BaseException],
              val: Optional[BaseException] = None,
              tb: Optional[TracebackType] = None) -> _T_co:
        return self.generator.throw(typ, val, tb)

    def map(self, generator: Generator[_T_cntr, Any, Any]) -> _V_co:
        for x in generator:
            self.set(x)

        return self.result


GeneratorFactory = Callable[..., Generator[_T_co, _T_cntr, _V_co]]


class SettableGeneratorFactory(Generic[_T_co, _T_cntr, _V_co]):
    default: _T_cntr
    _generator_factory: GeneratorFactory[_T_co, _T_cntr, _V_co]
    _latest: SettableGenerator[_T_co, _T_cntr, _V_co]

    @overload
    def __init__(
            self,
            generator_factory: GeneratorFactory[_T_co, _T_cntr, _V_co],
    ): ...

    @overload
    def __init__(
            self,
            generator_factory: GeneratorFactory[_T_co, _T_cntr, _V_co],
            default: _T_cntr,
    ): ...

    def __init__(
            self,
            generator_factory,
            default=Unset,
    ):
        self._generator_factory = generator_factory
        self.default = default

    def __call__(self, *args, **kwargs) \
            -> SettableGenerator[_T_co, _T_cntr, _V_co]:
        self._latest = SettableGenerator(
            self._generator_factory(*args, **kwargs),
            default=self.default,
        )
        return self._latest

    def map(self, generator: Generator[_T_cntr, Any, Any]) -> _V_co:
        for x in generator:
            self._latest.set(x)

        return self._latest.result

    def __get__(self, instance, owner=None):
        """Implement the descriptor protocol to make decorating instance
        method possible.

        """

        # Return a partial function with the first argument is the instance
        #   of the class decorated.
        return partial(self.__call__, instance)


@overload
def settable(
        *,
        default: _T_cntr = None,
) -> Callable[
    [GeneratorFactory[_T_co, _T_cntr, _V_co]],
    SettableGeneratorFactory[_T_co, _T_cntr, _V_co],
]: ...


@overload
def settable(
        generator: GeneratorFactory[_T_co, _T_cntr, _V_co],
        *,
        default: _T_cntr = None,
) -> SettableGeneratorFactory[_T_co, _T_cntr, _V_co]: ...


def settable(
        generator=None,
        *,
        default=None,
):
    if generator is None:
        return partial(settable, default=default)

    inner = wraps(generator)(
        SettableGeneratorFactory(generator, default=default)
    )

    return inner
