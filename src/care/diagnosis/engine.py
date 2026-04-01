"""Diagnosis engine — analyzes extracted data and produces readiness assessment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from care.conversation.llm import LLMProvider
from care.conversation.prompts import DIAGNOSIS_SYSTEM, RECOMMENDATION_SYSTEM
from care.conversation.session import ExtractedData


@dataclass
class DimensionScore:
    name: str
    score: float  # 0-5
    description: str
    gaps: list[str] = field(default_factory=list)


@dataclass
class Risk:
    description: str
    likelihood: str  # high, medium, low
    impact: str  # high, medium, low
    dimension: str


@dataclass
class DiagnosisResult:
    overall_score: float
    overall_readiness: str
    dimensions: list[DimensionScore]
    risks: list[Risk]
    gaps: list[dict[str, str]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "overall_readiness": self.overall_readiness,
            "dimensions": [
                {
                    "name": d.name,
                    "score": d.score,
                    "description": d.description,
                    "gaps": d.gaps,
                }
                for d in self.dimensions
            ],
            "risks": [
                {
                    "description": r.description,
                    "likelihood": r.likelihood,
                    "impact": r.impact,
                    "dimension": r.dimension,
                }
                for r in self.risks
            ],
            "gaps": self.gaps,
        }


@dataclass
class Recommendation:
    action: str
    why: str
    priority: str  # critical, important, nice-to-have
    phase: int  # 1-5
    phase_name: str
    dimension: str


@dataclass
class RecommendationResult:
    recommendations: list[Recommendation]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendations": [
                {
                    "action": r.action,
                    "why": r.why,
                    "priority": r.priority,
                    "phase": r.phase,
                    "phase_name": r.phase_name,
                    "dimension": r.dimension,
                }
                for r in self.recommendations
            ],
        }


async def diagnose(llm: LLMProvider, extracted: ExtractedData) -> DiagnosisResult:
    """Analyze extracted data and produce a CARE readiness diagnosis."""
    data_summary = _extracted_to_summary(extracted)

    raw = await llm.extract_json(
        messages=[
            {
                "role": "user",
                "content": (
                    f"Organization assessment data:\n{data_summary}\n\n"
                    "Produce a CARE governance readiness diagnosis with:\n"
                    "1. Maturity scores (0-5) for: Financial, Operational, Temporal, "
                    "Data_Access, Communication\n"
                    "2. Gaps (each with description and severity)\n"
                    "3. Risks (each with description, likelihood, impact, dimension)\n"
                    "4. Overall score (average of dimensions) and readiness statement\n"
                    "5. A plain-language summary (3-5 paragraphs) suitable for a business leader\n\n"
                    "JSON format:\n"
                    '{"overall_score": 3.2, "overall_readiness": "...", '
                    '"dimensions": [{"name": "Financial", "score": 3.5, '
                    '"description": "...", "gaps": ["..."]}], '
                    '"risks": [{"description": "...", "likelihood": "medium", '
                    '"impact": "high", "dimension": "Financial"}], '
                    '"gaps": [{"description": "...", "severity": "high"}], '
                    '"summary": "..."}'
                ),
            }
        ],
        system=DIAGNOSIS_SYSTEM,
    )

    dimensions = [
        DimensionScore(
            name=d["name"],
            score=d["score"],
            description=d["description"],
            gaps=d.get("gaps", []),
        )
        for d in raw.get("dimensions", [])
    ]

    risks = [
        Risk(
            description=r["description"],
            likelihood=r["likelihood"],
            impact=r["impact"],
            dimension=r.get("dimension", "General"),
        )
        for r in raw.get("risks", [])
    ]

    return DiagnosisResult(
        overall_score=raw.get("overall_score", 0),
        overall_readiness=raw.get("overall_readiness", ""),
        dimensions=dimensions,
        risks=risks,
        gaps=raw.get("gaps", []),
        summary=raw.get("summary", ""),
    )


async def recommend(
    llm: LLMProvider,
    extracted: ExtractedData,
    diagnosis_data: dict[str, Any] | None,
) -> RecommendationResult:
    """Generate actionable recommendations based on diagnosis."""
    data_summary = _extracted_to_summary(extracted)

    raw = await llm.extract_json(
        messages=[
            {
                "role": "user",
                "content": (
                    f"Organization data:\n{data_summary}\n\n"
                    f"Diagnosis:\n{diagnosis_data}\n\n"
                    "Generate prioritized recommendations. Each recommendation must include:\n"
                    "- action: What to do (one sentence, plain language)\n"
                    "- why: Why it matters (business impact)\n"
                    "- priority: critical / important / nice-to-have\n"
                    "- phase: 1-5 (Foundation / Observation / Limited / Expanded / Full)\n"
                    "- phase_name: The phase name\n"
                    "- dimension: Which CARE dimension it addresses\n\n"
                    "Also include a plain-language summary (2-3 paragraphs).\n\n"
                    "JSON format:\n"
                    '{"recommendations": [{"action": "...", "why": "...", '
                    '"priority": "critical", "phase": 1, "phase_name": "Foundation", '
                    '"dimension": "Financial"}], "summary": "..."}'
                ),
            }
        ],
        system=RECOMMENDATION_SYSTEM,
    )

    recommendations = [
        Recommendation(
            action=r["action"],
            why=r["why"],
            priority=r["priority"],
            phase=r["phase"],
            phase_name=r.get("phase_name", ""),
            dimension=r.get("dimension", "General"),
        )
        for r in raw.get("recommendations", [])
    ]

    return RecommendationResult(
        recommendations=recommendations,
        summary=raw.get("summary", ""),
    )


def _extracted_to_summary(extracted: ExtractedData) -> str:
    """Convert extracted data to a readable summary for LLM consumption."""
    parts = [f"Organization: {extracted.org_name or 'Unknown'}"]
    parts.append(f"Type: {extracted.org_type or 'Unknown'}")

    if extracted.departments:
        parts.append(f"Departments ({len(extracted.departments)}):")
        for d in extracted.departments:
            parts.append(f"  - {d.get('name', 'Unknown')}")

    if extracted.teams:
        parts.append(f"Teams ({len(extracted.teams)}):")
        for t in extracted.teams:
            parts.append(
                f"  - {t.get('name', 'Unknown')} (dept: {t.get('department', '?')})"
            )

    if extracted.financial_constraints:
        parts.append("Financial constraints:")
        for c in extracted.financial_constraints:
            parts.append(f"  - {c}")

    if extracted.operational_constraints:
        parts.append("Operational constraints:")
        for c in extracted.operational_constraints:
            parts.append(f"  - {c}")

    if extracted.data_access_constraints:
        parts.append("Data access constraints:")
        for c in extracted.data_access_constraints:
            parts.append(f"  - {c}")

    if extracted.communication_constraints:
        parts.append("Communication constraints:")
        for c in extracted.communication_constraints:
            parts.append(f"  - {c}")

    if extracted.bridges:
        parts.append("Cross-team coordination:")
        for b in extracted.bridges:
            parts.append(f"  - {b}")

    if extracted.current_ai_usage:
        parts.append(f"Current AI usage: {extracted.current_ai_usage}")
    if extracted.target_trust_posture:
        parts.append(f"Target trust posture: {extracted.target_trust_posture}")

    if extracted.gaps:
        parts.append(f"Information gaps ({len(extracted.gaps)}):")
        for g in extracted.gaps:
            parts.append(f"  - {g.get('description', g)}")

    return "\n".join(parts)
