from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class NoulQuestion:
    instructions: str
    true_criteria: str
    false_criteria: str

    def to_jev(self) -> dict[str, Any]:
        return {
            "type": "noul",
            "instructions": self.instructions,
            "criteria": {
                "true": self.true_criteria,
                "false": self.false_criteria,
            },
        }


class JevClient(Protocol):
    def score(self, state: dict[str, Any], questions: dict[str, dict[str, Any]]) -> dict[str, float]:
        """Return Noul probabilities keyed by question id."""
        ...
