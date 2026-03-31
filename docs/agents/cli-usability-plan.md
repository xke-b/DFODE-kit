# CLI Agent Usability Plan

## Scope
Improve only the DFODE-kit CLI surface for coding-agent use: deterministic behavior, explicit command dispatch, and cleaner automation semantics.

## Audit summary
Current CLI issues observed in `dfode_kit/cli/`:
- `main.py` does not return exit codes; command success/failure is not standardized for automation.
- command discovery in `command_loader.py` depends on dynamic module walk order, which is not guaranteed to be stable.
- command dispatch is implicit and only prints a fallback message for missing commands instead of failing predictably.
- command modules print ad hoc human-oriented status lines; there is no machine-readable output contract yet.
- there are currently no CLI-focused tests in the lightweight harness.

## Small first slice
1. Make command loading deterministic by sorting discovered command modules.
2. Refactor CLI entrypoint so `main(argv=None)` returns stable exit codes and `__main__` uses `SystemExit(main())`.
3. Make dispatch explicit: require `handle_command`, route errors to stderr, and return non-zero on handler failure.
4. Add lightweight tests for deterministic command ordering and CLI exit behavior.

## Deferred follow-ups
- Add a documented `--output {text,json}` contract for selected commands.
- Reduce noisy stdout from command implementations so result output is easier to parse.
- Add CLI smoke tests against small synthetic fixtures.
