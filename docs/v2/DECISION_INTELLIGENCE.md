# Decision Intelligence

Risk Copilot separates prediction, evidence, and human decision-making.

## Evidence graph

Project evidence is represented as a directed graph so the application can show relationships between delivery targets, issues, pull requests, and dependencies. The graph is inspectable and serializable for the web UI.

## Challenge workflow

A reviewer can challenge cited evidence. Challenged evidence is removed from the narrative layer, but the predictive score is not silently changed unless the underlying model inputs are explicitly updated.

## Decision Lab

The Decision Lab applies user-supplied feature scenarios to the same predictive model and compares the resulting score with the current score.

Scenario results are explicitly labeled as model-based and non-causal.

## Intervention tracking

Recommendations can be accepted, modified, or rejected. Later risk and delivery outcomes can be recorded. These are observational records and are not treated as proof that an intervention caused the result.

## Portfolio intelligence

The portfolio layer ranks delivery targets by current risk and surfaces rapidly worsening items separately from already-high-risk items.
