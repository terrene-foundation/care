"""Tests for PACT configuration generator."""

import yaml

from care.conversation.session import ExtractedData
from care.generator.pact_config import generate_pact_config


def test_generate_minimal_config():
    extracted = ExtractedData(org_name="Test Corp")
    result = generate_pact_config(extracted)
    assert result.yaml_content
    assert result.summary
    assert "Test Corp" in result.summary

    config = yaml.safe_load(result.yaml_content)
    assert config["organization"]["name"] == "Test Corp"
    assert config["genesis"]["authority"] == "test-corp-root"


def test_generate_with_departments():
    extracted = ExtractedData(
        org_name="Acme Inc",
        departments=[
            {"name": "Engineering"},
            {"name": "Marketing"},
        ],
        teams=[
            {"name": "Backend", "department": "Engineering"},
            {"name": "Content", "department": "Marketing"},
        ],
    )
    result = generate_pact_config(extracted)
    config = yaml.safe_load(result.yaml_content)
    assert len(config["departments"]) == 2
    assert config["departments"][0]["name"] == "Engineering"


def test_generate_with_constraints():
    extracted = ExtractedData(
        org_name="FinCo",
        financial_constraints=[{"limit": "$50,000 per transaction"}],
        data_access_constraints=[{"policy": "Customer data is confidential"}],
    )
    result = generate_pact_config(extracted)
    config = yaml.safe_load(result.yaml_content)
    assert config["root_envelope"]["financial"]["max_spend_usd"] == 50000.0


def test_generate_with_bridges():
    extracted = ExtractedData(
        org_name="BridgeCo",
        bridges=[
            {
                "type": "standing",
                "teams": ["Engineering", "Product"],
                "purpose": "Sprint planning",
            },
        ],
    )
    result = generate_pact_config(extracted)
    config = yaml.safe_load(result.yaml_content)
    assert len(config["bridges"]) == 1
    assert config["bridges"][0]["type"] == "standing"


def test_generate_with_trust_posture():
    extracted = ExtractedData(
        org_name="TrustCo",
        target_trust_posture="collaborative",
    )
    result = generate_pact_config(extracted)
    config = yaml.safe_load(result.yaml_content)
    assert config["organization"]["initial_posture"] == "shared_planning"


def test_generate_marks_gaps():
    extracted = ExtractedData(
        org_name="GapCo",
        gaps=[{"description": "Unknown financial limits"}],
    )
    result = generate_pact_config(extracted)
    config = yaml.safe_load(result.yaml_content)
    assert "_assessment_gaps" in config
    assert len(config["_assessment_gaps"]) == 1


def test_yaml_is_valid():
    extracted = ExtractedData(org_name="ValidCo")
    result = generate_pact_config(extracted)
    # Should parse without error
    config = yaml.safe_load(result.yaml_content)
    assert isinstance(config, dict)
