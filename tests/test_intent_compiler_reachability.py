from meta_controller import (
    Candidate,
    CandidateKind,
    EpistemicMode,
    EpistemicState,
    MetaControlIntentKind,
    MetaControllerEngine,
)


def _projection() -> EpistemicState:
    return EpistemicState(
        controller_ref="controller:test",
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


def test_hypothesis_without_capability_waits() -> None:
    candidate = Candidate(
        kind=CandidateKind.HYPOTHESIS,
        statement="compare two root-cause hypotheses",
        scope="controller:test",
        basis_refs=("event:hypothesis",),
        discriminates_between=("a", "b"),
        expected_discrimination=0.8,
    )

    frame = MetaControllerEngine().evaluate(_projection(), candidates=(candidate,))

    assert frame.selection.action is None
    assert frame.intent.kind is MetaControlIntentKind.WAIT


def test_problem_reframe_is_a_representation_revision_intent() -> None:
    candidate = Candidate(
        kind=CandidateKind.PROBLEM_REFRAME,
        statement="reframe around the unresolved target residual",
        scope="controller:test",
        basis_refs=("event:residual",),
        expected_discrimination=0.8,
    )

    frame = MetaControllerEngine().evaluate(_projection(), candidates=(candidate,))

    assert frame.selection.action is not None
    assert frame.intent.kind is MetaControlIntentKind.REVISE_REPRESENTATION
