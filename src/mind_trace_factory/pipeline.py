from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .jev import JevClient
from .models import FinalAnswer, GroundTruth, ScenarioArtifact, ThoughtTrace
from .thought_search import CandidateGenerator, SearchConfig, generate_trace
from .verifier import ClaimExtractor, VerificationReport, verify_final_answer, verify_scenario


StoryWriter = Callable[[GroundTruth], str]
AnswerWriter = Callable[[ScenarioArtifact, ThoughtTrace], str]


@dataclass
class PipelineResult:
    ground_truth: GroundTruth
    scenario: ScenarioArtifact
    scenario_verification: VerificationReport
    trace: ThoughtTrace
    answer: FinalAnswer
    answer_verification: VerificationReport


def run_pipeline(
    *,
    ground_truth: GroundTruth,
    story_writer: StoryWriter,
    claim_extractor: ClaimExtractor,
    candidate_generator: CandidateGenerator,
    answer_writer: AnswerWriter,
    jev: JevClient,
    search_config: SearchConfig = SearchConfig(),
) -> PipelineResult:
    scenario = ScenarioArtifact(text=story_writer(ground_truth))
    scenario_verification = verify_scenario(
        ground_truth=ground_truth,
        scenario=scenario,
        jev=jev,
        extract_claims=claim_extractor,
    )

    trace = generate_trace(
        ground_truth=ground_truth,
        scenario=scenario,
        generator=candidate_generator,
        jev=jev,
        config=search_config,
    )

    answer = FinalAnswer(text=answer_writer(scenario, trace))
    answer_verification = verify_final_answer(
        ground_truth=ground_truth,
        answer=answer,
        jev=jev,
        extract_claims=claim_extractor,
    )

    return PipelineResult(
        ground_truth=ground_truth,
        scenario=scenario,
        scenario_verification=scenario_verification,
        trace=trace,
        answer=answer,
        answer_verification=answer_verification,
    )
