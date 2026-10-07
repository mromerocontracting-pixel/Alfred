# Blueprint Reading Checklist — HVHZ Roofing Takeoffs
**Status: DRAFT. Marc to review.** Lines marked **[CONFIRM]** are my assumptions about how you work. Correct or delete them.

Use this checklist before every takeoff that starts from a plan set. It tells the estimator where each input lives, how to measure it, and how to check the result. Anything it can't find goes under **"Critical Missing Data for Miami-Dade Permitting"**, as the handoff prompt requires.

---

## Step 0 — Inventory the set
- [ ] Read the **sheet index** on the cover sheet. List every sheet in the PDF and flag any index sheet that isn't in the file.
- [ ] Record the set type (**bid / permit / revised / approved**), the latest revision number, and the date from the title block. If two sets exist for one job, use the newest revision and note the one you skipped.
- [ ] Record the job address, owner, architect/engineer, and the FBC edition stated on the cover.
- [ ] Note the roof scope: new construction, re-roof, or partial. For a re-roof, find the existing roof description and the number of layers to tear off.

## Step 1 — Verify scale before measuring anything
- [ ] Read the scale in the title block **and** under each drawing title. Details, enlarged plans, and the main roof plan often have different scales.
- [ ] **Check the scale against a printed dimension.** Measure a long dimension string (overall building length is best) and compare it to the written number. If they disagree by more than about 1%, stop and recalibrate.
- [ ] **Half-size trap:** sets printed or scanned to 11x17 from 24x36 are at half the stated scale. The dimension check above catches this.
- [ ] Drawings marked "NTS" (not to scale): use their written dimensions only. Never measure them.
- [ ] In Bluebeam, calibrate on the longest dimension you can find, not a short one.

## Step 2 — Where to find each required input

| Input | Primary sheet | Backup sheet | Notes |
|---|---|---|---|
| **Wind design data** (ultimate wind speed, Risk Category, Exposure Category, enclosure, internal pressure) | Cover sheet or S-0/S-1 general notes | Specs Div 01 or 07; engineer's wind load letter | Copy it word-for-word. Never assume a county default. |
| **Roof C&C pressures, Zones 1 / 1' / 2 / 3** | Wind pressure table or roof zone diagram (S or A sheets) | Engineer's calc package | If there's no table, list it as missing. Do not compute it ourselves. **[CONFIRM]** |
| **Mean roof height** | Elevations / building sections | Wall sections | ASCE 7: roof slope ≤ 10° (about ≤ 2⅛:12) → use eave height; steeper → average of eave and ridge height. Measure from grade. |
| **Pitch / slope** | Elevations (pitch triangle symbol); roof plan slope arrows | Building sections; truss drawings | Every plane can differ. Record pitch per plane, not one pitch for the whole roof. |
| **Deck type and thickness** | Structural framing plan / S-sheet notes | Wall sections; roof plan notes | Plywood/OSB thickness, concrete, steel deck gauge, or lightweight insulating concrete. Also record the sheathing nailing schedule. |
| **Framing** (truss/rafter spacing) | Structural framing plan | Truss shop drawings | Affects nail base and metal clip attachment. |
| **Roof outline, ridges, hips, valleys** | Roof plan (A-series) | Elevations to confirm | The roof plan outline is the drip edge line. **Never use the floor plan footprint.** |
| **Low-slope areas, drains, scuppers, crickets, overflows** | Roof plan | Plumbing roof drain plan / riser | Count primary and overflow drains separately. |
| **Roofing system and products** | Roof plan callouts; Specs Div 07 | Product approval schedule on the cover | Match each product to a preset ID (C1–M1, T1–T3, L1–L4, U-M1). |
| **NOA / FL# numbers** | Product approval schedule (cover or A-0) | Specs | Record the number and expiry date. Missing → Critical Missing Data. |
| **Edge metal, drip edge, coping, gravel stop** | Roof details (A-5xx series, or whatever the set uses) | Wall sections | Note material and gauge (galvanized, aluminum, copper) and face height. |
| **Roof-to-wall, parapets, counterflashing** | Wall sections; roof details | Elevations for parapet heights | Measure parapet LF and height to size base flashing. |
| **Penetrations** | Mechanical roof plan (curbs, condensers, exhaust fans); plumbing (vent stacks) | Electrical (conduit, solar); architectural (skylights) | Count by type: pipe vents, B-vents, exhaust fans, curbs (with sizes), skylights, conduit. |
| **Ventilation** (ridge vent, off-ridge, soffit) | Roof plan notes; energy calc | Specs | Note required NFA if stated. |

## Step 3 — Measure the geometry
Work plane by plane. Label each plane (R1, R2, …) on a marked-up roof plan so every number can be traced.

**Area**
- Plan area of each plane × pitch factor = true area. Sum the planes, then convert to SQ (÷ 100).
- Pitch factor = √(1 + (rise/12)²):

| Pitch | Factor | Pitch | Factor |
|---|---|---|---|
| 2:12 | 1.014 | 7:12 | 1.158 |
| 3:12 | 1.031 | 8:12 | 1.202 |
| 4:12 | 1.054 | 9:12 | 1.250 |
| 5:12 | 1.083 | 10:12 | 1.302 |
| 6:12 | 1.118 | 12:12 | 1.414 |

Low-slope roofs at ¼:12 have a factor of about 1.000. Use the plan area.

**Linear footage**
| Line | True length |
|---|---|
| Eave, ridge (level lines) | = plan length |
| Rake | plan length × pitch factor |
| Hip, valley | √(plan length² + rise²), where rise = the vertical drop along that hip or valley |

- Drip edge LF = eave LF + rake LF.
- L-flashing / step flashing / headwall LF: measure where each plane meets a wall.
- Record valley LF separately for open and closed valleys if the details differ.

**Mark as provisional** any dimension read off the drawing that isn't a printed dimension, any pitch inferred instead of labeled, and any area hidden or unclear on the plan.

## Step 4 — Cross-check before writing the takeoff
- [ ] Total roof area > building footprint (because of overhangs). If it's smaller, something is wrong.
- [ ] Drip edge LF ≈ roof outline perimeter on the roof plan.
- [ ] Each hip should end at a ridge or another hip. Each valley should run from an eave to a ridge or wall. A stray line usually means a misread plane.
- [ ] Compare against an EagleView/Hover report or Bluebeam export if one exists. Explain any area difference over 3%. **[CONFIRM tolerance]**
- [ ] Penetration count from the M/P sheets matches the symbols on the roof plan.
- [ ] Products called out on the plans match the NOA list and the preset IDs chosen.

## Step 5 — Stop conditions (go straight to "Critical Missing Data")
Any of these missing or unreadable:
- Pitch for any plane
- Mean roof height
- Risk Category or Exposure Category
- Zone 1 / 1' / 2 / 3 pressures
- Deck type
- NOA / FL# numbers for the roofing products
- A usable scale, i.e. the dimension check fails and there's no printed dimension to recover it

## Step 6 — Hand off to the takeoff
Pass the inputs from Steps 2–3 into the output format in `HVHZ_Estimator_Handoff_Prompt.md`. Also attach:
- the plane-by-plane area table (R1, R2, …)
- the list of provisional values
- the sheet number each input came from (e.g. "Pitch 5:12 — A-201 North Elevation")

---

## Open questions for Marc
1. Do you measure in Bluebeam today? If yes, what does your export look like? I'd build the agent to read it.
2. What area difference against EagleView do you accept before re-measuring?
3. When the plans have no pressure table, do you request one from the engineer, or use the roofing permit application's pressure calc?
4. Any sheets or details your local building departments always flag (Hialeah, Miami-Dade, Coral Gables, Miami Beach)? Those should go in Step 4.
