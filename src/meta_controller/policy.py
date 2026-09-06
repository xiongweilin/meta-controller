from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from portable_runtime.controller import (
    CognitiveController,
    ControllerDecision,
    ControllerDecisionKind,
    ControllerState,
    ControllerStatus,
    controller_capability_result,
    latest_controller_decision,
)

from .experience import ExperienceResolver
from .models import EpistemicState, EpistemicStateEstimator


class StagedMetaPolicy(ABC):
    """Reusable selection topology above Agent Kernel's canonical controller loop.

    Subclasses own domain-specific diagnosis, closure contents, Work proposal,
    revision classification and effect policy. This class only selects the next
    cognitive stage and supplies scoped experience hints.
    """

    controller: CognitiveController
    estimator = EpistemicStateEstimator()
    experience_resolver = ExperienceResolver()

    @property
    @abstractmethod
    def policy_ref(self) -> str: ...

    @abstractmethod
    def _diagnosis(self, state: ControllerState) -> ControllerDecision: ...

    @abstractmethod
    def _form_closure(
        self,
        state: ControllerState,
        diagnosis_result: dict[str, Any] | None,
    ) -> ControllerDecision: ...

    @abstractmethod
    def _propose_work(self, state: ControllerState) -> ControllerDecision: ...

    @abstractmethod
    def _current_revision(self, state: ControllerState) -> Any | None: ...

    @abstractmethod
    def _revision(self, state: ControllerState) -> ControllerDecision: ...

    @abstractmethod
    def _human_reopen_revision(self, state: ControllerState) -> ControllerDecision: ...

    def _has_human_followup(self) -> bool:
        value = getattr(self, "human_instruction", None)
        return isinstance(value, str) and bool(value.strip())

    def _accept_failed_diagnosis_as_unknown(self) -> bool:
        """Whether a failed/missing diagnosis may still close as UNKNOWN/read-only."""

        return False

    def epistemic_state(self, state: ControllerState) -> EpistemicState:
        return self.estimator.estimate(state)

    def experience_hints(self, state: ControllerState, *extra_tags: str) -> str:
        epistemic = self.epistemic_state(state)
        return self.experience_resolver.render((*epistemic.tags, *extra_tags))

    async def select(self, state: ControllerState) -> ControllerDecision:
        if state.status is ControllerStatus.CLOSED:
            raise ValueError("closed controller must not restart implicitly")

        if state.status is ControllerStatus.REOPEN_REQUIRED:
            return ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.REOPEN,
                reason="RevisionAssessment requires an explicit new cognitive episode",
            )

        if state.status is ControllerStatus.WAITING:
            if state.work_proposal_ref:
                if self._current_revision(state) is None:
                    return self._revision(state)
                if self._has_human_followup():
                    return self._human_reopen_revision(state)
                raise ValueError("waiting controller requires explicit follow-up after revision")
            return ControllerDecision(
                controller_ref=state.id,
                state_version=state.version,
                kind=ControllerDecisionKind.REOPEN,
                reason="resume an explicit cognitive wait without handed-off Work",
            )

        if state.active_closure_ref:
            return self._propose_work(state)

        last = latest_controller_decision(self.controller, state.id)
        if last is None or last.kind is ControllerDecisionKind.REOPEN:
            return self._diagnosis(state)

        if (
            last.kind is ControllerDecisionKind.INVOKE_CAPABILITY
            and last.parameters.get("phase") == "diagnosis"
        ):
            result = controller_capability_result(self.controller, state.id, last.id)
            if result is None:
                result = {
                    "status": "failed",
                    "message": "diagnosis returned no durable result",
                }
            succeeded = str(result.get("status", "")) == "succeeded"
            if not succeeded and not self._accept_failed_diagnosis_as_unknown():
                return ControllerDecision(
                    controller_ref=state.id,
                    state_version=state.version,
                    kind=ControllerDecisionKind.WAIT,
                    reason="diagnosis failed; wait rather than invent a cognitive closure",
                )
            return self._form_closure(state, result)

        raise ValueError(f"unexpected open controller stage after {last.kind.value}")
