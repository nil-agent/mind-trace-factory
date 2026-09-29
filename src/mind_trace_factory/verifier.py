from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .jev import JevClient, NoulQuestion
from .models import GroundTruth, Proposition, ScenarioArtifact, FinalAnswer


@dataclass(frozen=True)
class PropositionScore:
    proposition_id: str
    score: float


@dataclass(frozen=True)
class VerificationReport:
    forward: list[PropositionScore]
    reverse: list[PropositionScore]

    @property
    def min_forward(self) -> float:
        return min((x.score for x in self.forward), default=1.0)

    @property
    def min_reverse(self) -> float:
        return min((x.score for x in self.reverse), default=1.0)


ClaimExtractor = Callable[[str], list[str]]


def _forward_questions(propositions: list[Proposition], target_label: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in propositions:
        q = NoulQuestion(
            instructions=(
                f"Does {target_label} clearly communicate the proposition {p.id!r}: "
                f"{p.statement!r}? Judge semantic meaning rather than wording."
            ),
            true_criteria="The proposition is recoverable from the text without adding unsupported assumptions.",
            false_criteria="The proposition is missing, contradicted, or only recoverable by adding unsupported assumptions.",
        )
        out[p.id] = q.to_jev()
    return out


def verify_scenario(
    *,
    ground_truth: GroundTruth,
    scenario: ScenarioArtifact,
    jev: JevClient,
    extract_claims: ClaimExtractor,
) -> VerificationReport:
    required = ground_truth.required_story_propositions()
    forward_state = {
        "ground_truth": [p.__dict__ for p in required],
        "scenario": scenario.text,
    }
    forward_scores = jev.score(forward_state, _forward_questions(required, "the scenario"))

    claims = extract_claims(scenario.text)
    scenario.extracted_claims = claims
    reverse_questions: dict[str, dict] = {}
    for i, claim in enumerate(claims):
        key = f"claim_{i:03d}"
        reverse_questions[key] = NoulQuestion(
            instructions=(
                f"Is this scenario claim fully supported by the structured ground truth: {claim!r}? "
                "Treat unsupported additions and contradictions as false."
            ),
            true_criteria="The claim is licensed by the ground truth.",
            false_criteria="The claim contradicts the ground truth or introduces an unsupported factual assertion.",
        ).to_jev()

    reverse_state = {
        "ground_truth": [p.__dict__ for p in ground_truth.propositions],
        "scenario_claims": claims,
    }
    reverse_scores = jev.score(reverse_state, reverse_questions) if reverse_questions else {}

    return VerificationReport(
        forward=[PropositionScore(k, forward_scores[k]) for k in forward_scores],
        reverse=[PropositionScore(k, reverse_scores[k]) for k in reverse_scores],
    )


def verify_final_answer(
    *,
    ground_truth: GroundTruth,
    answer: FinalAnswer,
    jev: JevClient,
    extract_claims: ClaimExtractor,
) -> VerificationReport:
    key = ground_truth.answer_key()
    forward_state = {
        "answer_key": [p.__dict__ for p in key],
        "final_answer": answer.text,
    }
    forward_scores = jev.score(forward_state, _forward_questions(key, "the final answer"))

    claims = extract_claims(answer.text)
    reverse_questions: dict[str, dict] = {}
    for i, claim in enumerate(claims):
        qid = f"answer_claim_{i:03d}"
        reverse_questions[qid] = NoulQuestion(
            instructions=(
                f"Is this claim from the final answer compatible with the answer-key ground truth: {claim!r}? "
                "Respect uncertainty and information-access limits."
            ),
            true_criteria="The claim is supported by or appropriately qualified relative to the answer key.",
            false_criteria="The claim contradicts the answer key, leaks unavailable information, or overstates certainty.",
        ).to_jev()

    reverse_state = {
        "answer_key": [p.__dict__ for p in key],
        "answer_claims": claims,
    }
    reverse_scores = jev.score(reverse_state, reverse_questions) if reverse_questions else {}

    return VerificationReport(
        forward=[PropositionScore(k, forward_scores[k]) for k in forward_scores],
        reverse=[PropositionScore(k, reverse_scores[k]) for k in reverse_scores],
    )
