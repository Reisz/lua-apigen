build:
    uv run --script lua_lib_gen.py
    uvx --with sphinxcontrib-luadomain --from sphinx sphinx-build -M html doc dist
