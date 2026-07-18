# bagof-factories

Hint-based factories that build default values at runtime.

## Example

```pycon
>>> from bagof.factories import get_factory
>>> get_factory(list[int])()
[]
>>> get_factory(dict[str, int])()
{}
>>> get_factory(set[int])()
set()
>>> get_factory(int)()
0
>>> get_factory(int | None)()  # optional -> None
>>> get_factory(str)()
''
```

Abstract collection ABCs (`Sequence`, `Mapping`, `Set`, `Iterable`, ...),
numeric ABCs (`numbers.Integral`, `numbers.Real`, ...), enumerations, and
builtin/stdlib types whose constructor needs arguments (`range`, `slice`,
`memoryview`, `datetime`, `date`, `uuid.UUID`) are all handled too.
