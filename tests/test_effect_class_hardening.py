from meta_controller import (
    Candidate,
    CandidateKind,
    CapabilityAvailability,
    CapabilityBelief,
    EpistemicMode,
    EpistemicState,
    MetaControlIntentKind,
    MetaControllerEngine,
    WorkingSelfModel,
)


def test_candidate_cannot_downgrade_known_effectful_capability_to_read_only() -> None:
    projection = EpistemicState(
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
    candidate = Candidate(
        kind=CandidateKind.ACQUISITION,
        statement="probe by restarting the service",
        scope="controller:test",
        basis_refs=("event:proposal",),
        discriminates_between=("transient", "persistent"),
        expected_observable_difference="restart outcome differs",
        required_capabilities=("service.restart",),
        expected_discrimination=0.9,
        effect_class="read-only",
    )
    self_model = WorkingSelfModel(
        capabilities=(
            CapabilityBelief(
                capability_ref="service.restart",
                availability=CapabilityAvailability.AVAILABLE,
                effect_class="external-effect",
                basis_refs=("capability:catalog",),
            ),
        )
    )

    frame = MetaControllerEngine().evaluate(
        projection,
        candidates=(candidate,),
        self_model=self_model,
    )

    assert frame.intent.action is not None
    assert frame.intent.action.effect_class == "external-effect"
    assert frame.intent.kind is MetaControlIntentKind.EFFECTFUL_EXPERIMENT
