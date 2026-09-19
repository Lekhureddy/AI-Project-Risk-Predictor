# Test Plan

The core build uses automated checks for:

1. outcome-label boundaries and policy overrides
2. point-in-time reconstruction and future-data leakage rejection
3. end-to-end ingestion-to-feature processing
4. dataset quality, duplicate detection, label diversity, and training eligibility

The predictive model should not be trained until the data-quality gate passes on a defensible dataset.
