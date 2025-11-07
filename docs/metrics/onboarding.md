# Onboarding Time Baseline (SC-008)

Purpose: Provide a simple place to capture the baseline (T0) and post-CLI onboarding times to validate Success Criterion SC-008.

This document supports a lightweight, repeatable measurement so we can demonstrate a ≥50% reduction with the CLI.

## Who and What to Measure

- Participants: 3+ engineers familiar with Python but new to Restack
- Task: From blank repo to adding one workflow and one agent with passing tests
- Conditions: Record machine specs, OS, Python version, network notes

## Measurement Definitions

- Baseline (T0): Time to complete the task without using the CLI (manual setup)
- With CLI (T1): Time to complete the same task using quickstart + generators
- Target: T1 ≤ 0.5 × T0 (≥50% reduction)

Interim proxy gate (until T0 is captured): Create project + generate agent/workflow/function + run tests + pass `restack doctor` in ≤ 20 minutes on a clean machine following `quickstart.md`.

## Procedure

1. Read specs/001-restack-gen-cli/quickstart.md and follow environment setup
2. For Baseline (T0):
   - Do not use the CLI; set up manually
   - Implement 1 workflow + 1 agent + minimal tests
   - Record total time from start to passing tests
3. For With CLI (T1):
   - Use `restack new` + `restack g` commands
   - Implement equivalent workflow + agent + run tests
   - Record total time from start to passing tests
4. Repeat across 3+ participants; compute median times for T0 and T1

## Data Capture Template

Fill one block per participant. Keep raw notes concise and factual.

```
Participant: <Initials or ID>
Role/Background: <e.g., Python dev, no Restack experience>
Machine/OS/Python: <e.g., M2/16GB, macOS 15, Python 3.11.9>
Network Notes: <e.g., Corporate proxy>

Baseline (T0):
- Start: <YYYY-MM-DD HH:MM local>
- End:   <YYYY-MM-DD HH:MM local>
- Total: <minutes>
- Notes: <any blockers, confusion points>

With CLI (T1):
- Start: <YYYY-MM-DD HH:MM local>
- End:   <YYYY-MM-DD HH:MM local>
- Total: <minutes>
- Notes: <any blockers, confusion points>

Observations:
- Biggest time savers from CLI:
- Remaining friction:
- Suggestions:
```

## Reporting

- Compute medians across participants for T0 and T1
- Report reduction: `1 - (T1 / T0)`
- Keep the raw entries above for auditability

## Next Steps

- Schedule the T0/T1 study once the team is ready
- If the interim proxy gate fails (> 20 minutes), open issues to improve quickstart, generators, or doctor feedback

---

## Study Schedule (Initial)

This section proposes a lightweight schedule. Adjust dates as needed.

- Recruitment & Setup: 2025-11-07 to 2025-11-10
- Baseline (T0) Sessions: 2025-11-11 to 2025-11-12
- With CLI (T1) Sessions: 2025-11-13 to 2025-11-14
- Analysis & Report: 2025-11-17

Roles
- Coordinator: Project owner
- Participants: P1, P2, P3 (Python devs, new to Restack)

Tools
- Screen recording (optional), timer, clean Python 3.11+ environment, this repository checked out
- Follow `specs/001-restack-gen-cli/quickstart.md` for environment prep

Pre-Session Checklist
- [ ] Confirm clean machine or virtual environment
- [ ] Ensure network constraints (proxy) are documented
- [ ] Verify Python and pip versions
- [ ] Clone repo fresh and follow quickstart
- [ ] Prepare the specific workflow/agent task description

## Results Table (to fill during/after sessions)

| Participant | Machine/OS/Python | T0 Start | T0 End | T0 (min) | T1 Start | T1 End | T1 (min) | Reduction (1 - T1/T0) | Notes |
|-------------|--------------------|----------|--------|----------|----------|--------|----------|------------------------|-------|
| P1          |                    |          |        |          |          |        |          |                        |       |
| P2          |                    |          |        |          |          |        |          |                        |       |
| P3          |                    |          |        |          |          |        |          |                        |       |

Summary (Median)
- T0 median: <minutes>
- T1 median: <minutes>
- Reduction: <percent>

Privacy & Consent
- Avoid collecting personally identifiable information
- Share aggregated results only
