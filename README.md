# meta-controller

Replaceable epistemic/meta-control policy layer for [agent-kernel](https://github.com/xiongweilin/agent-kernel).

`meta-controller` owns evolving cognitive-selection policy. `agent-kernel` remains the stable semantic/runtime kernel and continues to own controller-state admissibility, cognitive closure, Work/Run, responsibility, authorization, verification, revision, recovery and provenance.

## Boundary

```text
ratio / operational experience
        |
        v
meta-controller
  epistemic state estimation
  current-use experience resolution
  staged cognitive selection
  search/retry/reopen guidance
  experience consolidation candidates
        |
        v
agent-kernel ControllerPolicy
        |
        v
Work / Run / Reality / Revision
```

Canonical separations:

```text
MetaPolicyState != CurrentTruth
ExperienceHint != CurrentDecision
HistoricalExperience != CurrentQualification
MetaControllerDecision != Work
MetaControllerDecision != ActionAuthorization
PolicyFailure != KernelSemanticFailure
```

## v0.1 scope

The first version deliberately implements only the reusable layer already evidenced by `ratio` and `control-plane`:

- `EpistemicStateEstimator` over durable Agent Kernel controller state;
- scoped experience rules for freshness, proxy/target separation, new-evidence-before-retry, UNKNOWN/no-effect, narrow-before-broaden, scoped generalization and representation-equivalence checks;
- `StagedMetaPolicy`, a reusable implementation of the canonical open/closure/work/revision/reopen selection topology;
- `ExperienceConsolidator`, which only promotes reality-grounded observations to scoped conditional experience candidates and never to authority or Kernel invariants.

It does **not** claim universal candidate generation, optimal search allocation, ontology induction, value arbitration or continual policy learning. Those are expected to evolve here without changing Agent Kernel unless a repeated failure proves a missing semantic invariant.

## Integration

Agent Kernel exposes a small external-policy loader and public controller history reads. A deployment can therefore load a policy factory by `module:attribute` without importing this project into the Kernel.

`control-plane` uses `StagedMetaPolicy` for generic controller-stage selection while retaining personal safety classification, Git/Docker/Prometheus effects, bounded repair policy and Feishu escalation as profile-specific logic.

## Experience discipline

Experience is retained only when it can change a future distinction, action choice, verification choice or stopping condition. One successful episode remains scoped and conditional. Historical experience can influence candidate generation and priors, but current use must be re-grounded in current scope/environment/evidence.

The initial rules are documented in `docs/experience-seeds.md` and represented in code by `meta_controller.experience.DEFAULT_EXPERIENCE_RULES`.
