# Assigned Jobs — Pending Start

The live tracker is in Notion. Notion is the source of truth; this file only explains how it works.

- **Database:** [Assigned Jobs — Pending Start](https://app.notion.com/p/ccc402267f50470ab48c18dc8d5ed944) (under Projects Hub)
- **Data source ID:** `collection://10fd5ca2-4caf-4bec-98c9-48fefbfe13a2`
- **Views:** default table, plus **Pipeline Board** (cards grouped by Stage)

## What goes here
Jobs that are **awarded but not yet started on the roof**. A lead or proposal stays in New Construction Tracker / Proposals & Plan Reviews until it's awarded. Then it gets a row here, linked back through **Source Record**. Once crews start, set Stage = **Started**. Day-to-day progress after that goes in Job Status Updates.

## Stages (in order)
Awarded → Contract Signed → NOC Signed → Permitting → Permit Approved → Materials Ordered → Scheduled → **Started**
Side stages: **On Hold** and **Cancelled**.

## Pre-start checklist (checkbox columns)
Contract Signed · Deposit Received · NOC Recorded · Permit Approved · NOAs / Submittals · Materials Ordered · Dumpster Ordered

## Each time something changes
1. Move **Stage** forward.
2. Tick any checklist boxes that are now done.
3. Add a dated line to the top of **Status Log** (`YYYY-MM-DD: what happened`).
4. Update **Next Action**, **Waiting On**, and **Last Update**.

A row whose Last Update is more than 14 days old needs a follow-up.

## Seeded 2026-11-11 (from New Construction Tracker rows marked Awarded)
| Job | Stage | Waiting on | Next action |
|---|---|---|---|
| 4161 Woodridge Rd (Jemko) | NOC Signed | Us | Record the NOC and submit the permit |
| 9032-9042 NW 38th St, Sunrise | Permitting | City / Permit | Confirm permit status (no update since 3/18/26) |
| 5951 SW 84 St (Biscayne Builders) | Awarded | Us | Confirm the underlayment option (MTS vs XFR) and send the contract |

Left out: 3100 Ohio St (already In Progress) and a blank "New Construction Project" row.
