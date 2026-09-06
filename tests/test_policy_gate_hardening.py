import pytest

from meta_controller import (
    ExperienceCandidate,
    ExperienceLifecycle,
    PolicyEvaluation,
    PolicyPromoter,
    PolicyVersion,
)


def _validated_shadow_rule():
    lifecycle = ExperienceLifecycle()
    first = lifecycle.from_candidate(
        ExperienceCandidate(
            summary="proxy success does not establish target recovery",
            scope="monitoring-backed repair",
            evidence_refs=("event:first",),
            policy_effects=("require independent target verification",),
            reopen_conditions=("target verification disagrees",),
        )
    )
    validated = lifecycle.validate(first, evidence_ref="event:second")
    promoter = PolicyPromoter()
    return promoter, promoter.shadow(promoter.propose(validated))


def test_repeated_validation_count_cannot_exceed_distinct_evidence() -> None:
    candidate = ExperienceCandidate(
        summary="single observation cannot count as repeated validation",
        scope="repair",
        evidence_refs=("event:only",),
        policy_effects=("change future search",),
        repeated_validation_count=2,
    )

    with pytest.raises(ValueError, match="distinct supporting evidence"):
        ExperienceLifecycle().from_candidate(candidate)


def test_duplicate_positive_validation_does_not_increase_confidence() -> None:
    lifecycle = ExperienceLifecycle()
    first = lifecycle.from_candidate(
        ExperienceCandidate(
            summary="bounded experience",
            scope="repair",
            evidence_refs=("event:first",),
            policy_effects=("change future search",),
        )
    )

    with pytest.raises(ValueError, match="new evidence_ref"):
        lifecycle.validate(first, evidence_ref="event:first")


def test_policy_promotion_requires_nonempty_replay_set() -> None:
    promoter, shadow = _validated_shadow_rule()
    evaluation = PolicyEvaluation(
        rule_ref=shadow.id,
        passed=True,
        replay_cases=0,
    )

    with pytest.raises(ValueError, match="at least one replay"):
        promoter.promote(PolicyVersion(version=1, rules=()), shadow, evaluation)
