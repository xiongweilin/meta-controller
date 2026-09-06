import pytest

from meta_controller import (
    Candidate,
    CandidateKind,
    EpistemicIssue,
    EpistemicIssueKind,
    EpistemicMode,
    EpistemicState,
    MetaControlIntentKind,
    MetaControllerEngine,
)


def _projection() -> EpistemicState:
    return EpistemicState(
        controller_ref="controller:current",
        state_version=1,
        mode=EpistemicMode.OPEN_EXPLORATION,
        candidate_count=0,
        open_issue_count=0,
        has_result=False,
        has_closure=False,
        has_work=False,
        has_revision=False,
        tags=frozenset({"open-exploration"}),
    )


def test_foreign_controller_candidate_is_rejected_from_frontier() -> None:
    foreign = Candidate(
        kind=CandidateKind.HYPOTHESIS,
        statement="foreign controller hypothesis",
        scope="controller:other",
        basis_refs=("event:foreign",),
        discriminates_between=("a", "b"),
        expected_discrimination=0.9,
    )

    frame = MetaControllerEngine().evaluate(_projection(), candidates=(foreign,))

    assert frame.frontier.candidates == ()
    assert len(frame.frontier.rejected) == 1
    assert frame.frontier.rejected[0].candidate_ref == foreign.id
    assert "scope" in frame.frontier.rejected[0].reason
    assert frame.intent.kind is MetaControlIntentKind.WAIT


def test_foreign_controller_issue_is_rejected_before_assessment() -> None:
    foreign = EpistemicIssue(
        kind=EpistemicIssueKind.MODEL_INTERNAL_UNKNOWN,
        statement="foreign controller uncertainty",
        scope="controller:other",
        basis_refs=("event:foreign",),
    )

    with pytest.raises(ValueError, match="scope does not match"):
        MetaControllerEngine().evaluate(_projection(), issues=(foreign,))
