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
        if not policy_ref.strip():
            raise ValueError("policy_ref must be non-empty")
        if intent.kind is MetaControlIntentKind.ACQUIRE_EVIDENCE:
            action = intent.action
            if action is None or action.capability is None:
                raise ValueError("evidence acquisition intent lacks a concrete capability")
            if action.effect_class != "read-only":
                raise ValueError("effectful epistemic actions cannot compile as direct cognition")
            decision = ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.INVOKE_CAPABILITY,
                capability=action.capability,
                instruction=action.instruction,
                policy_ref=policy_ref,
                reason=intent.reason,
            )
            return self._finalize(decision, intent, state, policy_ref)
        if intent.kind is MetaControlIntentKind.WAIT:
            decision = ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.WAIT,
                policy_ref=policy_ref,
                reason=intent.reason,
            )
            return self._finalize(decision, intent, state, policy_ref)
        if intent.kind is MetaControlIntentKind.REOPEN:
            decision = ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.REOPEN,
                policy_ref=policy_ref,
                reason=intent.reason,
            )
            return self._finalize(decision, intent, state, policy_ref)
        if intent.kind is MetaControlIntentKind.CLOSE:
            decision = ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.CLOSE,
                policy_ref=policy_ref,
                reason=intent.reason,
            )
            return self._finalize(decision, intent, state, policy_ref)
        if hooks is None:
            raise ValueError(f"{intent.kind.value} requires an explicit profile compiler hook")
        if intent.kind is MetaControlIntentKind.FORM_CLOSURE:
            decision = hooks.form_closure(intent, state)
            allowed = frozenset({ControllerDecisionKind.FORM_CLOSURE})
        elif intent.kind is MetaControlIntentKind.EFFECTFUL_EXPERIMENT:
            decision = hooks.effectful_experiment(intent, state)
            allowed = frozenset({ControllerDecisionKind.FORM_CLOSURE})
        elif intent.kind is MetaControlIntentKind.REVISE_REPRESENTATION:
            decision = hooks.revise_representation(intent, state)
            allowed = frozenset(
                {
                    ControllerDecisionKind.INVOKE_CAPABILITY,
                    ControllerDecisionKind.WAIT,
                }
            )
        else:
            raise ValueError(f"unsupported meta-control intent: {intent.kind.value}")
        if decision.kind not in allowed:
            raise ValueError(
                f"profile hook returned {decision.kind.value} for {intent.kind.value}; "
                "hook output violates the meta-control boundary"
            )
        return self._finalize(decision, intent, state, policy_ref)

    def _validate_binding(self, intent: MetaControlIntent, state: ControllerState) -> None:
        if intent.controller_ref != state.id or intent.kernel_state_version != state.version:
            raise ValueError("meta-control intent is stale or belongs to another controller")

    def _finalize(
        self,
        decision: ControllerDecision,
        intent: MetaControlIntent,
        state: ControllerState,
        policy_ref: str,
    ) -> ControllerDecision:
        if decision.controller_ref != state.id or decision.state_version != state.version:
            raise ValueError("profile hook decision is stale or belongs to another controller")
        parameters = dict(decision.parameters)
        parameters.update(
            {
                "meta_policy_version": intent.policy_version,
                "meta_intent": intent.kind.value,
                "meta_candidate_ref": intent.candidate_ref or "",
            }
        )
        return decision.model_copy(
            update={
                "policy_ref": policy_ref,
                "parameters": parameters,
            }
        )
