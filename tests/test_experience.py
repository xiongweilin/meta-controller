from __future__ import annotations

from portable_runtime.controller import ControllerState, ControllerStatus

from meta_controller import (
    ConsolidationStatus,
    EpistemicMode,
    EpistemicStateEstimator,
    ExperienceCandidate,
    ExperienceConsolidator,
    ExperienceResolver,
)


def test_state_estimator_projects_kernel_state_without_new_authority() -> None:
    state = ControllerState(
        id="controller:test",
        status=ControllerStatus.REOPEN_REQUIRED,
        version=7,
        candidate_refs=["candidate:a"],
        open_issue_refs=["issue:a"],
        last_result_ref="event:result",
        last_revision_ref="revision:a",
    )

    projected = EpistemicStateEstimator().estimate(state)

    assert projected.mode is EpistemicMode.REOPEN_REQUIRED
    assert projected.state_version == 7
    assert {"retry", "unknown", "candidate-space", "has-reality-result"} <= projected.tags


def test_retry_experience_requires_new_evidence() -> None:
    rules = ExperienceResolver().resolve({"retry"})

    assert [rule.id for rule in rules] == ["new-evidence-before-retry-v1"]
    assert "new observation" in " ".join(rules[0].directives)


def test_single_verified_episode_remains_scoped_conditional() -> None:
    assessment = ExperienceConsolidator().assess(
        ExperienceCandidate(
            summary="line ending noise can mimic semantic dirty state",
            scope="exact allowlisted Git repository with deterministic normalization check",
            evidence_refs=("event:verification",),
            policy_effects=("add representation-equivalence check",),
        )
    )

    assert assessment.status is ConsolidationStatus.SCOPED_CONDITIONAL


def test_experience_without_reality_evidence_is_rejected() -> None:
    assessment = ExperienceConsolidator().assess(
        ExperienceCandidate(
            summary="candidate lesson",
            scope="test scope",
            evidence_refs=(),
            policy_effects=("change retry policy",),
        )
    )

    assert assessment.status is ConsolidationStatus.REJECTED
