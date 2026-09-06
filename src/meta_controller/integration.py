from __future__ import annotations

from typing import Protocol

from portable_runtime.controller import (
    ControllerDecision,
    ControllerDecisionKind,
    ControllerState,
)

from .engine import MetaControlIntent, MetaControlIntentKind


class MetaControlCompilerHooks(Protocol):
    def form_closure(
        self,
        intent: MetaControlIntent,
        state: ControllerState,
    ) -> ControllerDecision: ...

    def effectful_experiment(
        self,
        intent: MetaControlIntent,
        state: ControllerState,
    ) -> ControllerDecision: ...

    def revise_representation(
        self,
        intent: MetaControlIntent,
        state: ControllerState,
    ) -> ControllerDecision: ...


class KernelDecisionCompiler:
    """Compile policy intent into a legal Kernel decision without minting Work/authority."""

    def compile(
        self,
        intent: MetaControlIntent,
        state: ControllerState,
        *,
        policy_ref: str,
        hooks: MetaControlCompilerHooks | None = None,
    ) -> ControllerDecision:
        self._validate_binding(intent, state)
        if intent.kind is MetaControlIntentKind.ACQUIRE_EVIDENCE:
            action = intent.action
            if action is None or action.capability is None:
                raise ValueError("evidence acquisition intent lacks a concrete capability")
            if action.effect_class != "read-only":
                raise ValueError("effectful epistemic actions cannot compile as direct cognition")
            return ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.INVOKE_CAPABILITY,
                capability=action.capability,
                instruction=action.instruction,
                parameters={"meta_candidate_ref": action.candidate_ref or ""},
                policy_ref=policy_ref,
                reason=intent.reason,
            )
        if intent.kind is MetaControlIntentKind.WAIT:
            return ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.WAIT,
                policy_ref=policy_ref,
                reason=intent.reason,
            )
        if intent.kind is MetaControlIntentKind.REOPEN:
            return ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.REOPEN,
                policy_ref=policy_ref,
                reason=intent.reason,
            )
        if intent.kind is MetaControlIntentKind.CLOSE:
            return ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.CLOSE,
                policy_ref=policy_ref,
                reason=intent.reason,
            )
        if hooks is None:
            raise ValueError(f"{intent.kind.value} requires an explicit profile compiler hook")
        if intent.kind is MetaControlIntentKind.FORM_CLOSURE:
            return hooks.form_closure(intent, state)
        if intent.kind is MetaControlIntentKind.EFFECTFUL_EXPERIMENT:
            return hooks.effectful_experiment(intent, state)
        if intent.kind is MetaControlIntentKind.REVISE_REPRESENTATION:
            return hooks.revise_representation(intent, state)
        raise ValueError(f"unsupported meta-control intent: {intent.kind.value}")

    def _validate_binding(self, intent: MetaControlIntent, state: ControllerState) -> None:
        if intent.controller_ref != state.id or intent.kernel_state_version != state.version:
            raise ValueError("meta-control intent is stale or belongs to another controller")
