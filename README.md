# bagof-factories

Hint-based factories that build default values at runtime.

## Example

```pycon
>>> from bagof.factories import get_factory
>>> get_factory(list[int])()
[]
>>> get_factory(dict[str, int])()
{}
>>> get_factory(int)()
0
>>> get_factory(int | None)()  # optional -> None
>>> get_factory(str)()
''
```
