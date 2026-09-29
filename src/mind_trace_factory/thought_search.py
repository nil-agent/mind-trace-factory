from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from .jev import JevClient, NoulQuestion
from .models import GroundTruth, ScenarioArtifact, ThoughtStep, ThoughtTrace


CandidateGenerator = Callable[[ScenarioArtifact, ThoughtTrace, int], list[str]]


@dataclass(frozen=True)
class SearchConfig:
    candidates_per_step: int = 8
    keep_fraction: float = 0.5
    min_steps: int = 3
    max_steps: int = 12
    ready_threshold: float = 0.85


def score_candidates(
    *,
    ground_truth: GroundTruth,
    scenario: ScenarioArtifact,
    trace: ThoughtTrace,
    candidates: list[str],
    jev: JevClient,
) -> list[tuple[str, float]]:
    questions = {}
    for i, candidate in enumerate(candidates):
        questions[f"candidate_{i:03d}"] = NoulQuestion(
            instructions=(
                f"Is candidate next thought {i} reasonable for the character to entertain now? "
                "It may be speculative or later rejected, but it must be psychologically and epistemically plausible "
                "given the scenario, ground truth, and thought trace so far."
            ),
            true_criteria="A plausible next cognitive move with appropriately calibrated uncertainty.",
            false_criteria="Implausible, contradictory, epistemically impossible, or unjustifiably certain.",
        ).to_jev()

    state = {
        "ground_truth": [p.__dict__ for p in ground_truth.propositions],
        "scenario": scenario.text,
        "thought_trace_so_far": trace.text,
        "candidates": {str(i): c for i, c in enumerate(candidates)},
    }
    scores = jev.score(state, questions)
    return [(c, scores[f"candidate_{i:03d}"]) for i, c in enumerate(candidates)]


def ready_to_answer(
    *,
    ground_truth: GroundTruth,
    scenario: ScenarioArtifact,
    trace: ThoughtTrace,
    jev: JevClient,
) -> float:
    question = NoulQuestion(
        instructions=(
            "Has the reasoning trace developed enough relevant reasoning to support a correct, appropriately uncertain "
            "final answer? Return true when further thought is unlikely to materially improve the answer."
        ),
        true_criteria="The trace is sufficient for a faithful final answer.",
        false_criteria="Important unresolved reasoning remains that is likely to materially affect the final answer.",
    )
    state = {
        "ground_truth": [p.__dict__ for p in ground_truth.propositions],
        "scenario": scenario.text,
        "thought_trace_so_far": trace.text,
    }
    return jev.score(state, {"ready": question.to_jev()})["ready"]


def generate_trace(
    *,
    ground_truth: GroundTruth,
    scenario: ScenarioArtifact,
    generator: CandidateGenerator,
    jev: JevClient,
    config: SearchConfig = SearchConfig(),
    rng: random.Random | None = None,
) -> ThoughtTrace:
    rng = rng or random.Random()
    trace = ThoughtTrace()

    while len(trace.steps) < config.max_steps:
        candidates = generator(scenario, trace, config.candidates_per_step)
        scored = sorted(
            score_candidates(
                ground_truth=ground_truth,
                scenario=scenario,
                trace=trace,
                candidates=candidates,
                jev=jev,
            ),
            key=lambda x: x[1],
            reverse=True,
        )
        keep_n = max(1, int(len(scored) * config.keep_fraction))
        survivors = scored[:keep_n]
        rng.shuffle(survivors)
        text, score = survivors[0]
        trace.steps.append(ThoughtStep(text=text, score=score))

        if len(trace.steps) >= config.min_steps:
            if ready_to_answer(
                ground_truth=ground_truth,
                scenario=scenario,
                trace=trace,
                jev=jev,
            ) >= config.ready_threshold:
                break

    return trace
