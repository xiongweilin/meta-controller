# Contributing

Contributions are welcome when they preserve the repository's ownership boundary.

`meta-controller` owns replaceable search, uncertainty, candidate-selection, representation-revision, closure-readiness, and policy-learning logic. It does not own Agent Kernel Work admission, execution authorization, provider execution, external-effect verification, deployment behavior, or runtime responsibility.

Before submitting a change:

1. Keep new policy outputs non-authority-bearing. A `MetaControlIntent` must not silently become Work or permission to act.
2. Add or update tests for boundary behavior, especially when a change affects effect classification, closure, replay, or policy promotion.
3. Prefer a concrete failure or decision problem over introducing a new abstraction only for conceptual completeness.
4. Run:

```powershell
uv sync --extra dev
uv run ruff check .
uv run mypy src --no-incremental --show-error-codes
uv run pytest -q
```

Architectural changes should explain which existing failure or decision problem the change addresses and why the current policy surface cannot express it safely.
