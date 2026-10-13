from typing import List

from ai_research_agent.research.evidence import Evidence


class EvidenceCollector:
    """Collect evidence records for a single research run."""

    def __init__(self):
        """Create an empty evidence collection."""
        self.evidences: List[Evidence] = []

    def add_evidence(self, evidence: Evidence):
        """Append one evidence record."""
        self.evidences.append(evidence)

    def get_all(self):
        """Return all collected evidence in insertion order."""
        return self.evidences

    def clear(self):
        """Remove all evidence from the collection."""
        self.evidences.clear()
