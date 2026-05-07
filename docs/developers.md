---
icon: simple/github
---

# Developers

Welcome to the contributor and developer guide for `MetroGYM`. This page helps you set up the project locally, rebuild the documentation, and extend the library.

!!! bug "Project Status"
    `MetroGYM` is actively evolving. Expect changes, and if you encounter issues, please open a [GitHub Issue](https://github.com/larrywhizz767-png/MetroGYM/issues).

---

## Installation & Troubleshooting

- **Python**: supported on `3.10` to `3.13`.
- **Package manager**: `uv` is the recommended workflow for this repository.
- **Core dependencies**: `pygame` and `beartype` are installed through `uv sync`.

!!! warning "Environment setup"
    If installation fails, start from a clean environment and run `uv sync` again.
    If documentation commands fail, install the docs dependencies before rebuilding the site.

---

## Install From Source MetroGYM

### Prerequisites
- **Python 3.10–3.13**: [Download](https://www.python.org/downloads/)
- **UV**: [Installation Guide](https://docs.astral.sh/uv/)

### Environment Setup

=== "Using UV <span class='tab-badge tab-badge--accent'>Recommended</span>"

    1. **Clone the repository**:

    ```bash
    git clone git@github.com:larrywhizz767-png/MetroGYM.git
    cd MetroGYM
    ```

    2. **Install dependencies**:

    ```bash
    uv sync
    ```

    3. **Verify the library build**:

    ```bash
    uv run python -m compileall src
    ```

    4. **Verify examples when relevant**:

    ```bash
    uv run python -m compileall examples
    ```

=== "Alternative Tools"

    Prefer `uv` for this repository. You can adapt the setup to another workflow, but the documented commands assume `uv`.

---

## Adding New Primitives

`MetroGYM` is built around explicit primitives and a validated pipeline. New public primitives should follow the existing structure closely.

=== "Primitive Contract"

    1. **Location**: add the implementation in the appropriate package under `src/metrogym/primitives/`.
    2. **Class Definition**: inherit from `BaseMetroPrimitive`.
    3. **Grouping**: assign the correct `primitive_group`.
    4. **Constructor State**: store public constructor arguments as attributes.
    5. **Build Step**: implement `transform(context)` so the primitive updates the shared build state explicitly.
    6. **Exports**: update the relevant `__init__.py` when the primitive should be public.

    **Example**:

    ```python
    from beartype import beartype

    from metrogym.templates.primitive import BaseMetroPrimitive


    @beartype
    class MyPrimitive(BaseMetroPrimitive):
        primitive_group = "control"

        def __init__(self, name: str):
            self.name = name

        def transform(self, context: object) -> object:
            return context
    ```

=== "Documentation Expectations"

    1. **Docstrings**: use Google-style public docstrings for user-facing objects.
    2. **API Pages**: keep API pages thin and let `mkdocstrings` render source documentation.
    3. **Navigation**: update `zensical.toml` when a new page should appear in the docs navigation.
    4. **Homepage Content**: keep homepage markup in `docs/overrides/home.html`.

!!! tip "Template Usage"
    Mirror a nearby primitive, keep validation explicit, and avoid compatibility shims or hidden fallback behaviour.

---

## Generating Documentation

Update and preview the documentation locally:

1. **Install the docs dependencies**:

```bash
uv sync --group docs
```

2. **Build the site**:

```bash
uv run zensical build
```

3. **Serve the site locally**:

```bash
uv run zensical serve
```

4. **Edit source files only**: make documentation changes in `docs/`, `zensical.toml`, and source docstrings, not in `site/`.
