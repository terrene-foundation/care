"""Diagnosis module — maturity scoring, gap analysis, recommendations."""

from care.diagnosis.engine import (
    DiagnosisResult,
    RecommendationResult,
    diagnose,
    recommend,
)

__all__ = ["DiagnosisResult", "RecommendationResult", "diagnose", "recommend"]
