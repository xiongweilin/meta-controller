from pathlib import Path

from meta_controller import (
    ExperienceCandidate,
    ExperienceLifecycle,
    MetaPolicyJournal,
    PolicyEvaluation,
    PolicyPromoter,
    PolicyVersion,
)


def test_meta_policy_journal_is_append_only_and_version_bound(tmp_path: Path) -> None:
    journal = MetaPolicyJournal(tmp_path / "meta-policy.db")
    event = journal.record(
        event_type="EpistemicAssessmentRecorded",
        controller_ref="controller:test",
        kernel_state_version=4,
        policy_version="policy-v1",
        payload={"mode": "open"},
        basis_refs=("event:reality",),
    )

    events = journal.list_events(controller_ref="controller:test")

    assert events == (event,)
    assert events[0].basis_refs == ("event:reality",)


def test_experience_requires_repeated_validation_before_policy_promotion() -> None:
    lifecycle = ExperienceLifecycle()
    first = lifecycle.from_candidate(
        ExperienceCandidate(
            summary="proxy health does not establish target health",
            scope="monitoring-backed repair",
            evidence_refs=("event:first",),
            policy_effects=("require independent target verification",),
            reopen_conditions=("target verification disagrees",),
        )
    )
    validated = lifecycle.validate(first, evidence_ref="event:second")
    promoter = PolicyPromoter()
    candidate = promoter.propose(validated)
    shadow = promoter.shadow(candidate)
    current = PolicyVersion(version=1, rules=())
    evaluation = PolicyEvaluation(
        rule_ref=shadow.id,
        passed=True,
        replay_cases=4,
        improvements=("blind retry count decreased",),
        evidence_refs=("replay:1",),
    )

    promoted = promoter.promote(current, shadow, evaluation)

    assert promoted.version == 2
    assert promoted.rules[0].status.value == "active"
