from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class Proposition:
    id: str
    statement: str
    kind: Literal[
        "world_fact",
        "observation",
        "belief",
        "goal",
        "relationship",
        "unknown",
        "answer_key",
    ] = "world_fact"
    required_in_story: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GroundTruth:
    propositions: list[Proposition]

    def required_story_propositions(self) -> list[Proposition]:
        return [p for p in self.propositions if p.required_in_story]

    def answer_key(self) -> list[Proposition]:
        return [p for p in self.propositions if p.kind == "answer_key"]


@dataclass
class ScenarioArtifact:
    text: str
    extracted_claims: list[str] = field(default_factory=list)


@dataclass
class ThoughtStep:
    text: str
    score: float | None = None


@dataclass
class ThoughtTrace:
    steps: list[ThoughtStep] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(step.text for step in self.steps)


@dataclass
class FinalAnswer:
    text: str
