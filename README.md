# mind-trace-factory

A research scaffold for generating **natural-language theory-of-mind traces** from synthetic, verifiable ground truth.

The core idea is to keep the training example natural while keeping verification structured:

```text
structured ground truth
        |
        v
  scenario writer
        |
        v
  natural scenario
        |
        +--> proposition-level round-trip verification
        |
        v
candidate next thoughts
        |
        v
   Jev scoring
        |
        v
 stochastic thought search
        |
        v
   final answer
        |
        v
proposition-level comparison
against answer ground truth
```

## Design principles

1. **Ground truth stays structured.** It is the source of verifiability.
2. **Training traces stay natural language.** No structured chain-of-thought representation is required in the dataset.
3. **Scenario rendering is checked in both directions.**
   - Every required ground-truth proposition should be represented by the story.
   - Every factual proposition asserted by the story should be licensed by the ground truth.
4. **Jev guides thought search, not the deployed model.**
   - Generate several plausible next thoughts.
   - Score each independently.
   - Cut the low-scoring tail.
   - Sample from the survivors.
   - Repeat until a stopping controller says the trace is ready for a final answer, subject to min/max step bounds.
5. **Final answers are verified proposition-by-proposition.** A projected answer key is compared semantically to the model answer in both directions.

## Repository shape

```text
src/mind_trace_factory/
  models.py          # typed artifacts passed between stages
  interfaces.py      # generator / Jev protocols
  jev_questions.py   # state + question payload builders
  verification.py    # bidirectional proposition checks
  thought_search.py  # iterative Jev-guided search
  pipeline.py        # orchestration
examples/
  maya_ground_truth.json
tests/
  test_verification.py
  test_thought_search.py
```

## The semantic round-trip

For a structured fact set `G` and a natural rendering `S`, we want an approximate semantic equality checked element-wise:

```text
for every g in G:  S entails g
for every s in claims(S): G licenses s
```

This is intentionally stronger than one aggregate "is this faithful?" judgment: failures retain proposition-level provenance.

For the final answer, the same pattern is applied to an **answer projection** `K = pi(G)`, rather than to the entire world state.

## Thought search

At step `t`:

1. Generate `N` candidate continuations from `scenario + trace_so_far`.
2. Ask Jev independently whether each is a reasonable thought for the character to entertain now.
3. Remove candidates below a configurable threshold or quantile.
4. Temperature-sample one survivor and append it.
5. Ask a separate Jev controller whether the trace is ready to answer.
6. Stop only after `min_steps`; force stop at `max_steps`.

The thought scorer is intentionally permissive: hypotheses may be entertained and later rejected. Final-answer verification is stricter.

## Status

This is an architectural scaffold. The real LLM adapter and Jev HTTP client are intentionally left behind small interfaces so we can iterate on prompts, models, and API details independently.
