from __future__ import annotations

import os

from .agents.narrative import (
    OllamaNarrativeProvider,
    TemplateNarrativeProvider,
    generate_verified_narrative,
)
from .evidence import build_evidence_index
from .evaluation import evaluate_narrative


def provider_from_environment():
    base_url = os.getenv("OLLAMA_BASE_URL")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    if base_url:
        return OllamaNarrativeProvider(model=model, base_url=base_url)
    return TemplateNarrativeProvider()


def generate_narrative(*, model_drivers: list[dict], evidence: list[dict], evidence_for_feature: dict[str, list[dict]]) -> dict:
    provider = provider_from_environment()
    index = build_evidence_index(evidence)
    payload = {
        "model_drivers": model_drivers,
        "evidence_for_feature": evidence_for_feature,
    }
    result = generate_verified_narrative(provider, payload, index)
    result["evaluation"] = evaluate_narrative(result, index).to_dict()
    result["provider"] = provider.__class__.__name__
    return result
