# meta-controller

[![CI](https://github.com/xiongweilin/meta-controller/actions/workflows/ci.yml/badge.svg)](https://github.com/xiongweilin/meta-controller/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](pyproject.toml)

A replaceable search, uncertainty, and cognitive-selection policy layer for [agent-kernel](https://github.com/xiongweilin/agent-kernel).

## Concrete decision problem

Suppose an incident has two plausible causes and one available read-only observation can distinguish them.

A generic agent loop can easily spend another turn repeating an equivalent query, broaden search without adding discriminating evidence, or jump into an effectful experiment before uncertainty is bounded. Meta Controller exists to choose the next information-bearing cognitive action and to decide when further exploration is no longer earning its cost.

A typical path is:

```text
2 plausible hypotheses
  -> score unresolved distinctions
  -> choose one discriminating read-only observation
  -> reject redundant search that adds no new evidence
  -> reassess uncertainty
  -> continue, revise the representation, or form temporary closure
  -> hand only a non-authority intent to Agent Kernel
```

If the useful next experiment is effectful, Meta Controller cannot silently treat it as a read. The experiment must go through Agent Kernel closure, Work, authorization, execution, and verification.

## What this layer controls

`agent-kernel` defines which state transitions are valid and owns Work, authorization, execution, verification, recovery, and durable responsibility. `meta-controller` decides what is worth investigating next inside those constraints.

In short:

```text
agent-kernel:
"Is this transition valid, authorized, durable, and recoverable?"

meta-controller:
"Given what we currently know, what should we inspect, compare, revise, or stop exploring next?"
```

`meta-controller` is deliberately non-authority-bearing. Its output can influence cognitive selection, but it cannot create Work, authorize effects, declare an external outcome verified, or bypass Agent Kernel state transitions.

## Why this is separate from the kernel

A stable runtime kernel should not have to encode one universal search strategy, uncertainty policy, candidate-generation method, or stopping rule.

Those policies may evolve rapidly. Different deployments may also want different answers to questions such as:

- Which unresolved issue has the highest information value?
- When is another observation worth its cost?
- When does repeated search stop adding discriminating evidence?
- Is the current representation of the problem itself blocking progress?
- When is a temporary cognitive closure justified?
- After a failed execution, should cognition reopen locally or at a deeper level?

Agent Kernel owns the invariants around what happens next. Meta Controller owns replaceable policy for choosing among admissible cognitive directions.

## Example

Suppose the agent has two plausible explanations for an incident and one available read-only check can distinguish them.

Meta Controller may conclude:

```text
current evidence is insufficient
-> inspect signal X before spending Work on Y
-> reject an equivalent repeated query that adds no new distinction
-> form closure only after the remaining uncertainty is bounded
```

It emits a `MetaControlIntent`. Agent Kernel still decides whether that intent can become a controller decision, closure, Work proposal, or runtime action.

An effectful experiment is never downgraded into a read-only epistemic action just because it would be useful for learning. It must go through the normal Kernel closure, Work, authorization, execution, and verification path.

## v0.2 architecture

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

## Canonical separations

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

## Boundary gate

The package does not import `control_plane.*`, `portable_runtime.providers.*`, or `portable_runtime.deployment.*`; register providers; call `runtime.run_capability`; or implement deployment, notification, or effect execution. Those concerns remain with Agent Kernel and explicit profile/runtime boundaries.

A failed or missing diagnosis defaults to `WAIT` and does not enter the `CognitiveClosure` path. The boundary is enforced by regression tests.

## Compatibility

`StagedMetaPolicy` remains the compatibility facade used by existing deployments. Existing `_diagnosis`, `_form_closure`, `_propose_work`, `_revision`, and reopen hooks retain their behavior. A profile can incrementally adopt the richer policy surface through:

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

Experience is retained only when it can change a future distinction, action choice, verification choice, or stopping condition. One successful episode remains scoped and conditional. Historical experience can influence candidate generation and priors, but current use must be re-grounded in current scope, environment, and evidence.

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

## Contributing and security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the architectural contribution boundary and [`SECURITY.md`](SECURITY.md) for private vulnerability reporting guidance.
