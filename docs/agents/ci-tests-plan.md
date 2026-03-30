# CI Harness Plan: first narrow slice

## Audit notes
- Harness scaffold is present and fast: `AGENTS.md`, `docs/agents/`, `Makefile`, pytest, and CI.
- Current lightweight tests cover file presence and a few utility behaviors.
- A reliability gap remains between local and CI verification: CI installs deps manually and runs `make check` / `make test` separately instead of the documented `make bootstrap-harness && make verify` loop.
- Agent docs topology is documented, but the harness does not yet verify that docs indices stay in sync as new agent docs are added.

## Narrow first slice
1. Make CI follow the same bootstrap + verify path documented for agents.
2. Add fast harness tests that lock this parity in place.
3. Add a docs-topology invariant so `docs/agents/README.md` stays aligned with actual agent docs.

## Out of scope
- Product/module refactors
- Heavy runtime/integration tests
- Training/data pipeline schema work
