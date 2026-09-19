# M0-M4 Test Plan

Three tests cover the first build batch:

1. `test_labels.py` — label boundaries, scope override and unsupported policy gap.
2. `test_temporal.py` — milestone membership replay, standard horizons and future-data leakage rejection.
3. `test_pipeline.py` — fake GitHub data through orchestration -> labels -> temporal snapshots -> features, including due-date proxy transparency.

All three must pass before M5 model work begins.
