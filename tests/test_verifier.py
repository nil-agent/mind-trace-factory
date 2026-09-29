from mind_trace_factory.models import FinalAnswer, GroundTruth, Proposition, ScenarioArtifact
from mind_trace_factory.verifier import verify_final_answer, verify_scenario


class FakeJev:
    def score(self, state, questions):
        return {key: 0.99 for key in questions}


def extract_claims(text: str) -> list[str]:
    return [x.strip() for x in text.split(".") if x.strip()]


def test_scenario_verification_is_proposition_level():
    gt = GroundTruth([
        Proposition("G01", "Alice saw Bob enter.", "observation"),
        Proposition("G02", "Alice did not hear the private conversation.", "observation"),
    ])
    scenario = ScenarioArtifact("Alice saw Bob enter. Alice did not hear the private conversation.")
    report = verify_scenario(
        ground_truth=gt,
        scenario=scenario,
        jev=FakeJev(),
        extract_claims=extract_claims,
    )
    assert [x.proposition_id for x in report.forward] == ["G01", "G02"]
    assert len(report.reverse) == 2


def test_final_answer_uses_answer_key_projection_only():
    gt = GroundTruth([
        Proposition("G01", "Secret world detail.", "world_fact"),
        Proposition("A01", "Alice remains uncertain.", "answer_key", required_in_story=False),
    ])
    report = verify_final_answer(
        ground_truth=gt,
        answer=FinalAnswer("Alice remains uncertain."),
        jev=FakeJev(),
        extract_claims=extract_claims,
    )
    assert [x.proposition_id for x in report.forward] == ["A01"]
