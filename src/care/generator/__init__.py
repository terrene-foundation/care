"""Generator module — produces PACT-compatible YAML from assessment data."""

from care.generator.pact_config import PactConfigResult, generate_pact_config

__all__ = ["PactConfigResult", "generate_pact_config"]
