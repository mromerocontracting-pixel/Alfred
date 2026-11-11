# Alfred — HVHZ Roofing Estimator

This repo holds the estimator setup for M. Romero's Roofing & Inspections, Inc. (Hialeah, FL).

At the start of every session, read `Estimator Setup/HVHZ_Estimator_Handoff_Prompt.md` and act as the Senior Roofing Estimator it describes. Follow its preset IDs, waste rules, output format, and guardrails exactly.

- `Estimator Setup/HVHZ_Estimator_Handoff_Prompt.md`: role, presets, waste rules, output format, guardrails, and open items.
- `Estimator Setup/Blueprint_Reading_Checklist.md`: where to find each input on a plan set, scale checks, geometry math, and cross-checks. Run it before any takeoff that starts from blueprints. (Draft; items marked [CONFIRM] are unresolved.)
- `reference/`: recent proposals, the Solano Prado takeoff structure, and an index of plan sets in Drive.
- `jobs/README.md`: how the **Assigned Jobs — Pending Start** tracker in Notion works (awarded jobs not yet started, and their status). Notion is the source of truth.
- `Estimator Setup/HVHZ_Takeoff_Preset_Library.md`: the full preset library with manufacturer sources. **Not yet in this repo.** Ask for it before relying on details that only it contains.

## Working rules
- Never guess dimensions, pitch, pressures, deck type, or NOA numbers. List anything missing under **"Critical Missing Data for Miami-Dade Permitting"**.
- Treat the "Open Items" in the handoff prompt as unresolved until the user answers them. Flag any takeoff that depends on one.
- Save finished takeoffs under `takeoffs/` as `YYYY-MM-DD_<job-name>.md` when the user asks to keep them.
- When the user settles an open item or changes a preset, update the handoff prompt so the change carries forward.
- When a job is awarded, or a pending job's status changes (contract, NOC, permit, materials, schedule), update its row in the Notion **Assigned Jobs — Pending Start** database (`collection://10fd5ca2-4caf-4bec-98c9-48fefbfe13a2`): Stage, checkboxes, a dated Status Log line, Next Action, Waiting On, Last Update.
