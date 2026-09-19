# Security and AI Safety

Risk Copilot is designed as read-only decision support.

## Controls implemented

- The narrative provider has no repository write tools.
- Retrieved evidence is treated as untrusted data, not instructions.
- Email-like PII and token-like secrets are redacted before evidence reaches the narrative layer.
- Every displayed narrative driver must pass deterministic evidence-ID and verbatim-quote verification.
- Unsupported claims are dropped.
- The system can abstain when evidence is insufficient.
- Scenario output is explicitly non-causal.
- Human approval remains required for delivery decisions.

## Deployment guidance

Production deployments should place GitHub tokens and model-provider credentials in a secret manager or deployment secret store. They must not be committed to the repository.

Enterprise deployment should add SSO/SAML, organization-level RBAC, tenant isolation, retention controls, encryption-key management, audit export, and formal compliance review. Those controls are product-roadmap items rather than falsely represented as implemented certifications.

## Red-team assets

The repository includes deterministic adversarial cases and a Promptfoo red-team configuration for indirect prompt injection, PII, and RBAC-style testing.
