from __future__ import annotations

import ast
import asyncio
from pathlib import Path

import pytest
from portable_runtime.controller import (
    CognitiveClosure,
    ControllerDecision,
    ControllerDecisionKind,
    ControllerState,
)

import meta_controller.policy as policy_module
from meta_controller import StagedMetaPolicy

SOURCE_ROOT = Path(__file__).parents[1] / "src" / "meta_controller"
FORBIDDEN_IMPORT_PREFIXES = (
    "control_plane",
    "portable_runtime.providers",
    "portable_runtime.deployment",
)
FORBIDDEN_OPERATION_NAMES = frozenset(
    {
        "register_provider",
        "register_providers",
        "register_capability_provider",
        "run_capability",
        "deploy",
        "notify",
        "send_notification",
        "emit_notification",
        "apply_effect",
        "execute_effect",
        "run_effect",
        "perform_effect",
        "effect",
    }
)
FORBIDDEN_IMPLEMENTATION_MODULES = frozenset(
    {"deployment", "effect", "effect_executor", "notification", "notifications"}
)


def _source_trees() -> list[tuple[Path, ast.Module]]:
    return [
        (path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
        for path in sorted(SOURCE_ROOT.rglob("*.py"))
    ]


def _is_forbidden_import(module: str) -> bool:
    normalized = module.lstrip(".")
    return any(
        normalized == prefix or normalized.startswith(f"{prefix}.")
        for prefix in FORBIDDEN_IMPORT_PREFIXES
    )


def _attribute_path(node: ast.AST) -> tuple[str, ...]:
    parts: list[str] = []
    current: ast.AST | None = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return tuple(reversed(parts))


def _forbidden_operations(tree: ast.AST) -> list[ast.AST]:
    violations: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            if node.name in FORBIDDEN_OPERATION_NAMES:
                violations.append(node)
        elif isinstance(node, ast.Attribute):
            path = _attribute_path(node)
            if path and path[-1] in FORBIDDEN_OPERATION_NAMES:
                violations.append(node)
        elif isinstance(node, ast.Call):
            path = _attribute_path(node.func)
            if path and path[-1] in FORBIDDEN_OPERATION_NAMES:
                violations.append(node)
    return violations


def test_meta_controller_source_stays_outside_runtime_boundaries() -> None:
    violations: list[str] = []
    for path, tree in _source_trees():
        if path.stem.lower() in FORBIDDEN_IMPLEMENTATION_MODULES:
            violations.append(f"{path}: forbidden implementation module")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if _is_forbidden_import(alias.name):
                        violations.append(f"{path}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if _is_forbidden_import(module):
                    violations.append(f"{path}:{node.lineno}: from {module} import ...")
                elif module == "portable_runtime":
                    for alias in node.names:
                        imported = f"{module}.{alias.name}"
                        if _is_forbidden_import(imported):
                            violations.append(
                                f"{path}:{node.lineno}: from {imported} import ..."
                            )
        for node in _forbidden_operations(tree):
            operation = getattr(node, "name", None) or ".".join(_attribute_path(node.func))
            violations.append(f"{path}:{node.lineno}: operation {operation}")

    assert violations == [], "meta-controller boundary violations:\n" + "\n".join(violations)


class _FailedDiagnosisPolicy(StagedMetaPolicy):
    def __init__(self) -> None:
        self.controller = object()
        self.closure_calls = 0

    @property
    def policy_ref(self) -> str:
        return "policy:test"

    def _diagnosis(self, state: ControllerState) -> ControllerDecision:
        raise AssertionError("diagnosis should not be selected in this regression")

    def _form_closure(
        self,
        state: ControllerState,
        diagnosis_result: dict[str, object] | None,
    ) -> ControllerDecision:
        self.closure_calls += 1
        closure = CognitiveClosure(
            controller_ref=state.id,
            controller_state_version=state.version,
            selected_direction="unsafe fallback closure",
            basis_refs=["diagnosis:failed"],
            acceptance_criteria=["must not be reachable"],
            verification_plan=["must not be reachable"],
            reopen_conditions=["must not be reachable"],
        )
        return ControllerDecision(
            controller_ref=state.id,
            state_version=state.version,
            kind=ControllerDecisionKind.FORM_CLOSURE,
            closure=closure,
            reason="unsafe fallback closure",
        )

    def _propose_work(self, state: ControllerState) -> ControllerDecision:
        raise AssertionError("work proposal should not be selected in this regression")

    def _current_revision(self, state: ControllerState) -> object | None:
        raise AssertionError("revision should not be selected in this regression")

    def _revision(self, state: ControllerState) -> ControllerDecision:
        raise AssertionError("revision should not be selected in this regression")

    def _human_reopen_revision(self, state: ControllerState) -> ControllerDecision:
        raise AssertionError("human follow-up should not be selected in this regression")

    def _accept_failed_diagnosis_as_unknown(self) -> bool:
        """A legacy override must not bypass the failed-diagnosis gate."""

        return True


def test_failed_diagnosis_waits_and_cannot_form_cognitive_closure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = ControllerState(id="controller:test", version=3)
    diagnosis = ControllerDecision(
        controller_ref=state.id,
        state_version=state.version,
        kind=ControllerDecisionKind.INVOKE_CAPABILITY,
        capability="diagnose.target",
        parameters={"phase": "diagnosis"},
    )
    monkeypatch.setattr(
        policy_module,
        "latest_controller_decision",
        lambda controller, ref: diagnosis,
    )
    monkeypatch.setattr(
        policy_module,
        "controller_capability_result",
        lambda controller, ref, decision_ref: {
            "status": "failed",
            "message": "provider unavailable",
        },
    )

    policy = _FailedDiagnosisPolicy()
    selected = asyncio.run(policy.select(state))

    assert selected.kind is ControllerDecisionKind.WAIT
    assert selected.closure is None
    assert policy.closure_calls == 0
