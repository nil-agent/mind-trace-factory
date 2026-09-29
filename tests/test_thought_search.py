import random

from mind_trace_factory.models import GroundTruth, Proposition, ScenarioArtifact
from mind_trace_factory.thought_search import SearchConfig, generate_trace


class FakeJev:
    def score(self, state, questions):
        if "ready" in questions:
            steps = state["thought_trace_so_far"].count("\n") + bool(state["thought_trace_so_far"])
            return {"ready": 1.0 if steps >= 2 else 0.0}
        return {key: 0.9 - i * 0.1 for i, key in enumerate(questions)}


def generator(scenario, trace, n):
    return [f"candidate {len(trace.steps)}.{i}" for i in range(n)]


def test_trace_stops_when_ready_after_min_steps():
    gt = GroundTruth([Proposition("G01", "A fact.")])
    trace = generate_trace(
        ground_truth=gt,
        scenario=ScenarioArtifact("A scenario."),
        generator=generator,
        jev=FakeJev(),
        config=SearchConfig(candidates_per_step=4, keep_fraction=0.5, min_steps=2, max_steps=8),
        rng=random.Random(1),
    )
    assert len(trace.steps) == 2
