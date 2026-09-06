import pytest
from portable_runtime.controller import (
    ControllerDecision,
    ControllerDecisionKind,
    ControllerState,
)

from meta_controller import (
    EpistemicAction,
    EpistemicActionKind,
    KernelDecisionCompiler,
    MetaControlIntent,
    MetaControlIntentKind,
)


class _UnsafeHooks:
    def form_closure(self, intent, state):
        return ControllerDecision(
            controller_ref=state.id,
            state_version=state.version,
            kind=ControllerDecisionKind.WAIT,
            reason="wrong hook output",
        )

    def effectful_experiment(self, intent, state):
        return ControllerDecision(
            controller_ref=state.id,
            state_version=state.version,
            kind=ControllerDecisionKind.INVOKE_CAPABILITY,
            capability="service.restart",
            reason="unsafe direct effect attempt",
        )

    def revise_representation(self, intent, state):
        return ControllerDecision(
            controller_ref="controller:other",
            state_version=state.version,
            kind=ControllerDecisionKind.WAIT,
            reason="foreign controller",
        )


def _state() -> ControllerState:
    return ControllerState(id="controller:test", version=3)


def test_effectful_experiment_hook_cannot_compile_direct_capability_invocation() -> None:
    state = _state()
    action = EpistemicAction(
        kind=EpistemicActionKind.TEST,
        candidate_ref="candidate:effect",
        instruction="restart service to discriminate hypotheses",
        capability="service.restart",
        effect_class="external-effect",
    )
    intent = MetaControlIntent(
        controller_ref=state.id,
        kernel_state_version=state.version,
        policy_version="meta-policy-v7",
        kind=MetaControlIntentKind.EFFECTFUL_EXPERIMENT,
        reason="effectful test selected",
        action=action,
        candidate_ref=action.candidate_ref,
    )

    with pytest.raises(ValueError, match="violates the meta-control boundary"):
        KernelDecisionCompiler().compile(
            intent,
            state,
            policy_ref="profile:test",
            hooks=_UnsafeHooks(),
        )


def test_hook_decision_cannot_target_another_controller() -> None:
    state = _state()
    action = EpistemicAction(
        kind=EpistemicActionKind.RE_REPRESENT,
        candidate_ref="candidate:representation",
        instruction="revise root-cause partition",
    )
    intent = MetaControlIntent(
        controller_ref=state.id,
        kernel_state_version=state.version,
        policy_version="meta-policy-v7",
        kind=MetaControlIntentKind.REVISE_REPRESENTATION,
        reason="representation revision selected",
        action=action,
        candidate_ref=action.candidate_ref,
    )

    with pytest.raises(ValueError, match="another controller"):
        KernelDecisionCompiler().compile(
            intent,
            state,
            policy_ref="profile:test",
            hooks=_UnsafeHooks(),
        )


def test_direct_read_compilation_persists_meta_policy_provenance() -> None:
    state = _state()
    action = EpistemicAction(
        kind=EpistemicActionKind.OBSERVE,
        candidate_ref="candidate:read",
        instruction="inspect bounded evidence",
        capability="reason.generate",
        effect_class="read-only",
    )
    intent = MetaControlIntent(
        controller_ref=state.id,
        kernel_state_version=state.version,
        policy_version="meta-policy-v7",
        kind=MetaControlIntentKind.ACQUIRE_EVIDENCE,
        reason="bounded read selected",
        action=action,
        candidate_ref=action.candidate_ref,
    )

    decision = KernelDecisionCompiler().compile(
        intent,
        state,
        policy_ref="profile:test",
    )

    assert decision.kind is ControllerDecisionKind.INVOKE_CAPABILITY
    assert decision.policy_ref == "profile:test"
    assert decision.parameters["meta_policy_version"] == "meta-policy-v7"
    assert decision.parameters["meta_intent"] == "acquire-evidence"
    assert decision.parameters["meta_candidate_ref"] == "candidate:read"
