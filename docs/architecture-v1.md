# Meta-controller epistemic control architecture v1

Status: implementation baseline
Owner: `meta-controller`

## Purpose

`meta-controller` is the replaceable, non-authority-bearing epistemic control plane above Agent Kernel. It decides how cognition should proceed: what remains unresolved, which candidate distinctions are live, which observation or representation change has the highest current discriminating value, when temporary closure is justified, and where reality feedback suggests revision.

It does not own current truth, Work admission, execution authorization, external effects, verified outcomes, standing-responsibility lifecycle, or Agent Kernel legal transitions.

## Cross-repository ownership

```text
ratio
  semantic framework / candidate structures / theory
        |
        | operationalization evidence and policy seeds
        v
meta-controller
  epistemic assessment / candidate frontier / search allocation
  representation revision / working self-model / closure readiness
  revision diagnosis / scoped experience / policy evolution
        |
        | version-bound MetaControlIntent -> ControllerDecision
        v
agent-kernel
  legal controller state / CognitiveClosure / WorkProposal
  persistent responsibility / authorization / Work / Run
  verification / RevisionAssessment / recovery / provenance
        |
        v
profile deployments such as control-plane
  observations / providers / domain constraints / effect boundaries
        |
        v
Reality
```

Framework text is never runtime authority. Meta-controller state is policy state and never current truth. Agent Kernel remains the semantic/runtime authority for legal transitions and responsibility boundaries.

## Canonical separations

The following are non-negotiable meta-controller invariants:

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

Existing Agent Kernel separations remain authoritative downstream.

## Runtime loop

```text
Kernel ControllerState
      -> project durable coordination state
      -> EpistemicAssessment
      -> diagnose issues / uncertainty
      -> detect StructuralTension
      -> generate and qualify Candidates
      -> CandidateFrontier
      -> update/check WorkingSelfModel
      -> select EpistemicAction
          -> read-class observation -> Kernel invoke-capability -> evidence -> reassess
          -> representation revision -> new frontier -> reassess
          -> effectful epistemic experiment -> closure/work/authorization path
      -> ClosureReadiness
          -> keep exploring / wait / escalate
          -> or form bounded CognitiveClosure
      -> Work / Run / verification in Agent Kernel
      -> RevisionDiagnosis
          -> local disposition
          -> or explicit reopen with representation/candidate-space change
      -> reassess
```

A reopen is not a blind repetition. A policy should prefer a new discriminating observation, a changed representation, a changed candidate frontier, or an explicitly justified scope/problem change before repeating an equivalent cognitive pass.

## Learning loop

```text
verified episode
  -> ExperienceCandidate
  -> scoped conditional experience
  -> repeated independent validation
  -> PolicyRuleCandidate
  -> replay / shadow evaluation
  -> explicit policy-version promotion
  -> future selection
```

An experience or policy rule must retain scope, evidence boundary, known negative evidence, reopen conditions and version/provenance. Current use is always re-grounded.

## Kernel promotion gate

A meta-controller policy concept is promoted into Agent Kernel only when repeated independent failures show that the Kernel cannot preserve a necessary semantic distinction regardless of policy quality. Algorithm quality, convenience, vocabulary preference, or explanatory precision are insufficient reasons to change Kernel contracts.

## Implementation phases

1. Durable policy journal and policy-version identity.
2. Typed epistemic issues and assessments.
3. Candidate frontier and generator/qualification seams.
4. Structural tension and search allocation.
5. Representation revision and working self-model.
6. Closure readiness and revision planner.
7. Experience lifecycle and policy promotion/evaluation.
8. Compatibility facade and profile migration.
9. Replay/conformance scenarios proving the complete loop.
