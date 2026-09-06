# meta-controller

Replaceable epistemic/meta-control policy layer for [agent-kernel](https://github.com/xiongweilin/agent-kernel).

`meta-controller` owns evolving cognitive-selection policy. `agent-kernel` remains the stable semantic/runtime kernel and continues to own controller-state admissibility, cognitive closure, Work/Run, responsibility, authorization, verification, revision, recovery and provenance.

## v0.2 boundary

```text
ratio / operational experience
        |
        v
meta-controller
  durable non-authority policy journal
  epistemic issue / uncertainty assessment
  structural-tension detection
  candidate generation / qualification / frontier
  working self-model
  search allocation / epistemic action selection
  representation revision
  closure readiness
  revision diagnosis
  experience consolidation / policy promotion / replay
        |
        v
MetaControlIntent
        |
        v
Agent Kernel ControllerPolicy / explicit profile compiler hooks
        |
        v
Work / Run / Reality / Revision
```

Canonical separations:

```text
ReasonerOutput != QualifiedCandidate
Candidate != CurrentTruth
EpistemicAssessment != CurrentTruth
EpistemicAssessment != ControllerState
EpistemicAssessment != CognitiveClosure
EpistemicAssessment != Work
EpistemicAssessment != ActionAuthorization
HistoricalExperience != CurrentQualification
StructuralTension != DeepRevision
RepresentationCandidate != RepresentationAdoption
WorkingSelfModel != RuntimeAuthority
MetaControlIntent != ControllerDecision
MetaControlIntent != Work
MetaControlIntent != ActionAuthorization
OneSuccessfulEpisode != UniversalPolicy
CognitiveClosure != CandidateSpaceComplete
```

Agent Kernel's downstream separation contracts remain authoritative.

## Closed epistemic loop

```text
Kernel ControllerState
        |
        v
EpistemicState projection
        |
        v
EpistemicAssessment
  typed issues / uncertainty / structural tension
        |
        v
Candidate generation + qualification
        |
        v
CandidateFrontier
        |
        v
WorkingSelfModel + SearchBudget
        |
        v
EpistemicAction selection
   /           |             \
read       representation    effectful test
 |             revision          |
 |                |              |
invoke-          new         CognitiveClosure
capability      frontier      -> WorkProposal
 |                |              |
 +------ reality / evidence -----+
                 |
                 v
          reassessment
                 |
                 v
          ClosureReadiness
            /         \
      continue         close temporarily
                         |
                         v
                   Agent Kernel Work
                         |
                         v
                 verification/reality
                         |
                         v
                 RevisionDiagnosis
                    /       \
                 local     deep
                           |
                       explicit reopen
                           |
                    changed evidence,
                    representation,
                    candidate frontier
                    or problem framing
```

A reopen is not a blind repeat. Search policy rejects an equivalent action when its redundancy key has already been consumed and no new discriminating difference is represented.

Effectful epistemic experiments are never compiled as direct read-class cognition. They must go through the normal Kernel closure/Work/authorization path.

## Core modules

- `epistemic.py` — typed epistemic issues, uncertainty profile, structural tension and assessment.
- `candidates.py` — candidate types, qualification, frontier dominance filtering and residual-driven structural generation.
- `self_model.py` — fallible capability/resource beliefs; never authority.
- `representation.py` — explicit, versioned representation mutation candidates and application.
- `planning.py` — epistemic actions, hard search budgets, closure readiness and revision diagnosis.
- `engine.py` — assembles a `MetaControlFrame` and emits a non-authority `MetaControlIntent`.
- `integration.py` — version-bound compilation to Agent Kernel decisions; closure/effect/representation intents require explicit profile hooks.
- `journal.py` — append-only SQLite policy journal bound to controller/version/policy identity.
- `policy_learning.py` — scoped experience lifecycle, shadow evaluation and explicit policy promotion.
- `replay.py` — deterministic structural replay metrics for policy promotion gates.

The design and ownership baseline is in [`docs/architecture-v1.md`](docs/architecture-v1.md).

## Compatibility

`StagedMetaPolicy` remains the compatibility facade used by existing deployments. Existing `_diagnosis`, `_form_closure`, `_propose_work`, `_revision` and reopen hooks retain their behavior. A profile can incrementally adopt the richer control plane through:

```python
frame = policy.meta_control_frame(
    state,
    issues=...,
    tensions=...,
    candidates=...,
    self_model=...,
    budget=...,
)
```

This evaluates policy state only. It does not create Work or execution authority.

## Experience discipline

Experience is retained only when it can change a future distinction, action choice, verification choice or stopping condition. One successful episode remains scoped and conditional. Historical experience can influence candidate generation and priors, but current use must be re-grounded in current scope/environment/evidence.

Promotion lifecycle:

```text
verified episode
  -> ExperienceCandidate
  -> scoped conditional experience
  -> repeated validation
  -> PolicyRule candidate
  -> shadow / replay evaluation
  -> explicit PolicyVersion promotion
```

A policy may evolve without changing Agent Kernel. A distinction reaches Agent Kernel only when repeated real failures show that the Kernel cannot preserve a necessary semantic invariant regardless of policy quality.

## Existing experience seeds

The current reusable seeds remain:

- freshness before reuse;
- new discriminating evidence before retry;
- proxy/target separation;
- UNKNOWN does not authorize effect;
- narrow before broaden;
- scoped generalization;
- representation-equivalence checks.

See [`docs/experience-seeds.md`](docs/experience-seeds.md).

## Development

```powershell
uv sync --extra dev
uv run ruff check .
uv run mypy src --no-incremental --show-error-codes
uv run pytest -q
```
