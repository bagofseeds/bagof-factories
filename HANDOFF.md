# `bagof-factories` — build handoff

Context brief for continuing the `bagof-factories` work in a fresh session
(the originating session could not reach the `neuroscales` source repos — see
**Access** below). Everything here is derived from the in-scope precedents
(`bagof-things`, `bagof-converters`, `bagof-hints`); the only missing input is
the actual factory source, which lives in `neuroscales/abczarr` (and
`neuroscales/brainhops`).

Originating session: <https://claude.ai/code/session_01Uwk4bPStfQjD2QWNxURXUR>

---

## Goal

1. Create `bagof-factories` from **`neuroscales/abczarr/_core/auto/factories`**,
   exactly as **`bagof-converters`** was created from
   `neuroscales/abczarr/_core/auto/converters`.
2. Then look at **`neuroscales/brainhops/_ext/struct/factories`** and add the
   **missing** factories — **only the genuinely required ones**, i.e. NOT those
   whose behaviour is already exactly covered by the base/common factories
   ported in step 1.

## Access (why this is a handoff)

- This session was owner-tier-locked to `bagofseeds` / `balbasty`. Mid-session
  `add_repo` cannot cross into `neuroscales` (v1 limit), and both the git proxy
  and the GitHub API deny `neuroscales/abczarr` + `neuroscales/brainhops`.
- `brainhops` is **private**; the org has no Claude GitHub App (not addable on
  Claude Max).
- Resolutions (pick one), all confirmed viable:
  - **`claude --teleport session_01Uwk4bPStfQjD2QWNxURXUR`** → run locally with
    your own git credentials; clone `abczarr` + private `brainhops` directly.
    (Local runs unsandboxed by default; `/sandbox` to confine.)
  - **Fork/mirror into `bagofseeds`** (`bagofseeds/abczarr`, private
    `bagofseeds/brainhops`) → same owner tier → `add_repo` works in a session.
  - **New web session** seeded with `neuroscales/abczarr` +
    `neuroscales/brainhops` + `bagofseeds/bagof-factories` +
    `bagofseeds/bagof-converters` + `bagofseeds/bagof-hints` as initial sources.

## Current repo state (IMPORTANT)

`bagof-factories` was seeded as a **verbatim copy of the `bagof-things`
template** — it is still branded `things`:

- `pyproject.toml` → `name = "bagof-things"`, only dep `typing_extensions>=4.13`.
- `src/bagof/things/__init__.py` (must become `src/bagof/factories/…`).
- Minimal `docs/`, `tests/test_import.py`, `zensical.toml`, `.devcontainer/`.
- **No `.github/workflows/*` committed** (the template ships without the CI set).

So step 0 is **retargeting `things` → `factories`** and pulling in the fuller
`bagof-converters` structure.

---

## The pattern (from `bagof-converters`, the exact sibling precedent)

`bagof-converters` = `abczarr/_core/auto/converters`, restructured as a
`bagof.*` PEP 420 namespace package. Mirror it 1:1.

### Dependencies (`pyproject.toml`)
```toml
requires-python = ">=3.8"
dependencies = [
    "typing_extensions >= 4.13",
    "bagof-hints @ git+https://github.com/bagofseeds/bagof-hints.git",
    "bagof-core-magic @ git+https://github.com/bagofseeds/bagof-core-magic.git",
]
```
- **`bagof-hints`** supplies `bagof.hints.typevars.co` (`T`, `NONE`, `NoneType`,
  `STR`, `INT`, `NUMBER`, `ITERABLE`, `MAPPING`, `SEQUENCE`, `TUPLE`, …),
  `bagof.hints.array.ArrayLike`, and `bagof.hints.{numpy,cupy,dask}`.
- **`bagof-core-magic`** supplies `bagof.core.magic` (`MagicHint`, `UNSET`,
  `get_from_registry`, `safe_isinstance`, `safe_issubclass`) — the hint-dispatch
  registry the **base** class is built on.
- **TBD from source:** if `auto/factories` constructs converters, add
  `bagof-converters @ git+…` too. Confirm by reading the imports.

### Module layout (`src/bagof/factories/`)
`bagof-converters` has: `__init__.py`, `base.py`, `common.py`, `collections.py`,
`numbers.py`, `strings.py`, `enums.py`, `exceptions.py`, `numpy.py`, `cupy.py`,
`dask.py`, `pandas.py`, plus helpers `_arrays.py`, `_compat.py`. Port whatever
set `auto/factories` actually has — the module names/split should follow the
source, not be forced to match converters.

- **`base.py`** is the crux. Converters' `base.py` defines `Converter`,
  `ConverterRegistry`, `register_converter`, `get_converter`,
  `get_converter_class`, `wrap_converter`, via a metaclass over `MagicHint`.
  The factories base will be the analogous `Factory` / `FactoryRegistry` /
  `register_factory` / `get_factory` / … — **port it from
  `abczarr/.../factories`, do NOT hand-derive it from converters.** These
  "base factories" are the baseline that the brainhops step measures against.
- **`__init__.py`** uses the shared bag idiom (identical in `bagof-hints` and
  `bagof-converters`): a numpydoc "Modules" docstring, an `__all__` seed, then
  `from . import (…)`, `from .<mod> import *` + `from .<mod> import __all__ as
  __all_<mod>`, then `__all__ += __all_<mod>` per module. Array-lib modules
  (`numpy`/`cupy`/`dask`) guard the real library import internally (try/except)
  so importing the package never hard-requires the lib.

### Tooling / config to copy from `bagof-converters/pyproject.toml`
```toml
[tool.ruff]
line-length = 79
target-version = "py38"
[tool.ruff.lint]
select = ["ANN", "B", "E", "F", "I", "UP", "W"]
ignore = ["ANN002", "ANN003", "ANN401", "UP006", "UP035"]   # 3.8-safe UP subset
[tool.coverage.run]
source = ["bagof.factories"]
[tool.coverage.report]
exclude_also = ["if tx.TYPE_CHECKING:", "if tx.TYPE_CHECKING or"]
```
Plus `versioningit` writing `src/bagof/factories/_version.py`;
`[tool.setuptools.packages.find] include = ["bagof*"] namespaces = true`;
classifiers 3.8–3.12 + `Typing :: Typed`; codespell config.

### CI (copy the full set from `bagof-converters/.github/workflows/`)
`lint`, `test`, `test-matrix`, `coverage`, `docs`, `test-and-publish`,
`publish-pypi`, `publish-on-release`, and the four `*-on-push` wrappers — all
thin wrappers delegating to `bagofseeds/actions/.github/workflows/*.yaml@main`.
Add `codecov.yml` (project+patch `target auto`, `threshold 1%`). The
`.devcontainer/devcontainer.json` should grant write to `bagofseeds/bagof-hints`
and `bagofseeds/bagof-core-magic` (git deps installed from source in CI).

### Docs
`docs/api/<mod>.md` per public module (mkdocstrings `::: bagof.factories.<mod>`),
`docs/api/index.md`, `docs/index.md`, `docs/requirements.txt`,
`docs/stylesheets/extra.css`, and `zensical.toml` whose inventories include
`https://bagofseeds.github.io/bagof-hints/objects.inv` (add bag-core-magic /
converters inventories if referenced). Sprout logo / bagof green — match the
other bagof bags, not a new theme.

### Tests
`tests/test_<mod>.py` per module + `tests/test_import.py`,
`tests/test_typevars.py`, `tests/requirements.txt`. Port the source's own tests
if any; otherwise mirror the converters test shape.

---

## Step 2 — brainhops factories (the selective part)

Read `neuroscales/brainhops/_ext/struct/factories`. For each factory there:

- **Drop** it if the ported base/common factories already reproduce its
  behaviour exactly (the base `Factory` + generic registry dispatch covers most
  "make an X from a hint" cases generically).
- **Port** only factories with genuinely distinct behaviour not expressible via
  the base ones. When in doubt, flag it to the user rather than silently port or
  drop — same judgement call as the diffeo de-vendor equivalence work.
- Watch for the copy-paste `__all__` bugs seen in the brainhops `*_typing`
  originals during the `bagof-hints` array work (byte-identical `__all__`
  blocks promising names never defined) — don't carry those over.

## Verification (local, before pushing)
- Fresh venv, `pip install -e ".[test]"` (+ `bagof-hints`, `bagof-core-magic`
  from git), `python -c "import bagof.factories; print(bagof.factories.__version__)"`.
- `ruff check` + `ruff format --check` + `codespell` clean (line-length 79).
- `pytest` green. `numpy`/`dask` installable on CPU; `cupy` intentionally absent
  (its library-present branch is type-checked only) — mirror converters'
  `tests/requirements.txt`.
- Confirm PEP 420 coexistence: `import bagof.hints` and `import bagof.factories`
  in one venv both work.
- Open a **PR** (do not push straight to `main`) and confirm lint/test/coverage
  go green, same as the `bagof-hints` docstring PR (#6) workflow.

## Reference material (all readable in a properly-seeded session)
- Precedent: `bagofseeds/bagof-converters` (structure, base.py, CI, docs, tests).
- Template: `bagofseeds/bagof-things`.
- Dep API: `bagofseeds/bagof-hints` (typevars/array/numpy/cupy/dask), and
  `bagofseeds/bagof-core-magic` (`MagicHint`).
- Shared CI: `bagofseeds/actions/.github/workflows/*@main`.
- Source (needs neuroscales access): `abczarr/_core/auto/factories`,
  `abczarr/_core/auto/converters` (to see the exact transform),
  `brainhops/_ext/struct/factories`.
