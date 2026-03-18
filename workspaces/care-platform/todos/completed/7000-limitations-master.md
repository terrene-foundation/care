# Resolve All v0.1.0 Known Limitations

**Created**: 2026-03-16
**Status**: IN PROGRESS
**Scope**: 10 limitations from RT15 ship-readiness report

| #   | Limitation                           | Severity | Fix                                  |
| --- | ------------------------------------ | -------- | ------------------------------------ |
| L1  | Bridge approver uses substring check | HIGH     | Proper team membership lookup        |
| L2  | Unbounded collections in 4 modules   | HIGH     | Add maxlen bounds                    |
| L3  | No DM task description length limit  | HIGH     | Add max_length=10000                 |
| L4  | WebSocket not wired in Flutter       | HIGH     | Create WebSocket provider            |
| L5  | CORS not validated for HTTPS in prod | MEDIUM   | Validate origins in production       |
| L6  | No request body size limit           | MEDIUM   | Add body size middleware             |
| L7  | Flutter widget tests minimal         | MEDIUM   | Add widget tests for key screens     |
| L8  | Posture upgrade not in web dashboard | MEDIUM   | Add upgrade action button            |
| L9  | Flat sparkline trends                | LOW      | Compute trends from audit timestamps |
| L10 | LLM pricing hardcoded                | LOW      | Move to config/env                   |
