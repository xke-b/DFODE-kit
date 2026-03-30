# Verification Loop

The repository should provide a fast path for agents to validate changes before opening a PR.

## Required local loop
0. `make bootstrap-harness` — create local `uv`-managed `.venv` with lightweight verification deps
1. `make check` — fast syntax validation (`compileall`)
2. `make test` — lightweight pytest suite
3. `make verify` — all of the above

## What belongs in lightweight tests
- Pure utility behavior
- File/schema/layout invariants
- Documentation or harness expectations
- Fast parser or serializer behavior

## What should be added later
- CLI smoke tests
- Training config schema validation tests
- Dataset contract validation tests
- Small synthetic end-to-end smoke runs

## Rule
If a rule matters for future agent-generated diffs, prefer encoding it as:
1. a test,
2. a script target,
3. CI,
4. documentation.
