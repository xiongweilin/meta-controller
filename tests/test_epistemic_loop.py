from meta_controller import (
    Candidate,
    CandidateKind,
    CapabilityAvailability,
    CapabilityBelief,
    EpistemicIssue,
    EpistemicIssueKind,
    EpistemicIssueStatus,
    EpistemicMode,
    EpistemicState,
    MetaControlIntentKind,
    MetaControllerEngine,
    RepresentationMutationKind,
    RepresentationReviser,
    RepresentationRevisionCandidate,
    RepresentationState,
    RevisionPlanner,
    SearchBudget,
    WorkingSelfModel,
)


def _projection() -> EpistemicState:
    return EpistemicState(
        controller_ref="controller:test",
        state_version=3,
        mode=EpistemicMode.OPEN_EXPLORATION,
        candidate_count=0,
        open_issue_count=0,
        has_result=True,
        has_closure=False,
        has_work=False,
        has_revision=False,
        tags=frozenset({"open-exploration", "has-reality-result"}),
    )


def test_engine_selects_new_discriminating_observation() -> None:
    candidate = Candidate(
        kind=CandidateKind.ACQUISITION,
        statement="query independent target health",
        scope="controller:test",
        basis_refs=("event:residual",),
        discriminates_between=("provider-failure", "target-failure"),
        expected_observable_difference="target health differs across the live hypotheses",
        required_capabilities=("monitor.target.health",),
        expected_discrimination=0.9,
        decision_relevance=1.0,
        redundancy_key="target-health",
    )
    self_model = WorkingSelfModel(
        capabilities=(
            CapabilityBelief(
                capability_ref="monitor.target.health",
                availability=CapabilityAvailability.AVAILABLE,
                can_observe=("target-health",),
                basis_refs=("provider:health",),
            ),
        )
    )

    frame = MetaControllerEngine().evaluate(
        _projection(),
        candidates=(candidate,),
        self_model=self_model,
    )

    assert frame.intent.kind is MetaControlIntentKind.ACQUIRE_EVIDENCE
    assert frame.intent.action is not None
    assert frame.intent.action.capability == "monitor.target.health"


def test_engine_blocks_equivalent_blind_retry() -> None:
    candidate = Candidate(
        kind=CandidateKind.ACQUISITION,
        statement="repeat same observation",
        scope="controller:test",
        basis_refs=("event:first",),
        discriminates_between=("a", "b"),
        expected_observable_difference="new target evidence",
        required_capabilities=("monitor.target.health",),
        expected_discrimination=0.8,
        redundancy_key="same-pass",
    )
    self_model = WorkingSelfModel(
        capabilities=(
            CapabilityBelief(
                capability_ref="monitor.target.health",
                availability=CapabilityAvailability.AVAILABLE,
            ),
        )
    )

    frame = MetaControllerEngine().evaluate(
        _projection(),
        candidates=(candidate,),
        self_model=self_model,
        used_redundancy_keys=frozenset({"same-pass"}),
    )

    assert frame.intent.kind is MetaControlIntentKind.WAIT
    assert frame.selection.action is None


def test_effectful_epistemic_test_does_not_compile_as_read_cognition() -> None:
    candidate = Candidate(
        kind=CandidateKind.EXPERIMENT,
        statement="restart bounded canary to distinguish transient state",
        scope="controller:test",
        basis_refs=("event:contradiction",),
        discriminates_between=("stale-state", "persistent-failure"),
        expected_observable_difference="canary outcome differs after bounded restart",
        required_capabilities=("service.restart.canary",),
        expected_discrimination=0.8,
        effect_class="internal-reversible",
    )
    self_model = WorkingSelfModel(
        capabilities=(
            CapabilityBelief(
                capability_ref="service.restart.canary",
                availability=CapabilityAvailability.AVAILABLE,
                effect_class="internal-reversible",
            ),
        )
    )

    frame = MetaControllerEngine().evaluate(
        _projection(),
        candidates=(candidate,),
        self_model=self_model,
    )

    assert frame.intent.kind is MetaControlIntentKind.EFFECTFUL_EXPERIMENT


def test_closure_requires_resolved_or_deferred_decision_relevant_issues() -> None:
    candidate = Candidate(
        kind=CandidateKind.HYPOTHESIS,
        statement="adopt bounded working hypothesis",
        scope="controller:test",
        basis_refs=("event:evidence",),
        discriminates_between=("a", "b"),
        expected_discrimination=0.0,
    )
    issue = EpistemicIssue(
        kind=EpistemicIssueKind.MODEL_INTERNAL_UNKNOWN,
        statement="low relevance unknown remains",
        scope="controller:test",
        basis_refs=("event:evidence",),
        decision_relevance=0.2,
        status=EpistemicIssueStatus.DEFERRED,
    )
    frame = MetaControllerEngine().evaluate(
        _projection(),
        issues=(issue,),
        candidates=(candidate,),
        adopted_candidate_ref=candidate.id,
        acceptance_criteria=("bounded criterion",),
        verification_plan=("independent verification",),
        reopen_conditions=("contradicting reality",),
    )

    assert frame.intent.kind is MetaControlIntentKind.FORM_CLOSURE


def test_representation_revision_is_explicit_and_versioned() -> None:
    state = RepresentationState(scope="incident", factors=("dirty",), basis_refs=("event:a",))
    candidate = RepresentationRevisionCandidate(
        representation_ref=state.id,
        mutation=RepresentationMutationKind.SPLIT_FACTOR,
        parameters=(("source", "dirty"), ("left", "semantic-change"), ("right", "noise")),
        reason="surface dirty conflates semantic change and representation noise",
        basis_refs=("event:line-ending",),
        expected_discriminating_change="semantic change and line-ending noise become separable",
    )

    result = RepresentationReviser().apply(state, candidate)

    assert result.applied is True
    assert result.representation is not None
    assert result.representation.version == 2
    assert set(result.representation.factors) == {"semantic-change", "noise"}


def test_revision_planner_refuses_blind_execution_retry() -> None:
    assessment = MetaControllerEngine().assessor.assess(
        _projection(),
        policy_version="test-v1",
        basis_refs=("event:failed-run",),
    )

    diagnosis = RevisionPlanner().diagnose(
        assessment,
        new_discriminating_evidence=False,
        verification_present=True,
    )

    assert diagnosis.recommended_disposition == "acquire-evidence"


def test_budget_is_a_hard_gate_not_a_risk_tradeoff() -> None:
    candidate = Candidate(
        kind=CandidateKind.HYPOTHESIS,
        statement="expensive comparison",
        scope="controller:test",
        basis_refs=("event:a",),
        discriminates_between=("a", "b"),
        expected_discrimination=1.0,
        estimated_cost=10.0,
    )
    frame = MetaControllerEngine().evaluate(
        _projection(),
        candidates=(candidate,),
        budget=SearchBudget(max_cost=1.0),
    )
    assert frame.selection.action is None
