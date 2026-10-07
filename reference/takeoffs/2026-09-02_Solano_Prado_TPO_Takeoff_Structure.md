# Solano Prado (Coral Gables) — TPO Material Takeoff: Template Structure
Source: [Google Sheet](https://docs.google.com/spreadsheets/d/1LMXiBD3DgcTZMM04_TcJQaWMrwQc4lz3z5nONkIO4j8/edit) (latest of two copies; the older one is `1DuFGK8BUCCZaSW6gX2zgmk_khhGRgnxQn8O3jC3YXPU`).

The Drive connector returned the layout plus sample rows, not every cell. Line items below section 2 (flashing, edge metal, fasteners, accessories) are in the sheet but were not captured here. Open the sheet for the full list.

## System
GAF EverGuard TPO 60-mil, fully adhered, heat-welded seams · Deck: **Concrete** · Insulation: fully adhered tapered ISO, priced by GulfEagle Supply quote **Job #26-2402** (dated 8/26/2026, expired 9/25/2026).

## Workbook layout (three tabs)

### 1. Assumptions (A1:C40)
- Header: job, system, reference quote.
- Legend: **blue text = editable input** (the takeoff recalculates); **yellow fill = open item, confirm before ordering**.
- `JOB INPUTS` table with columns **Input | Value | Source / Note**.

### 2. TPO Takeoff (A1:H40)
Columns: **Item | Product / SKU | Qty Needed | Unit | Order Qty | Unit Cost ($) | Ext. Cost ($) | Basis / Notes**

Grouped by numbered section. Captured rows:

| Item | Product / SKU | Qty Needed | Unit | Order Qty | Unit Cost | Ext. Cost | Basis / Notes |
|---|---|---|---|---|---|---|---|
| **1. TAPERED ISO INSULATION — PRICED SEPARATELY** | | | | | | | |
| Tapered ISO insulation, fully adhered | 2" fill + 3" tapered base, ISO, panel SKUs 48D1/48D2/48F1 + 2.0" flat | 187.0 | SQ | lump | — | $21,201 | GulfEagle lump sum, Job #26-2402. Itemizing by SKU needs GulfEagle's panel cut list. |
| **2. TPO MEMBRANE & BONDING ADHESIVE — FIELD** | | | | | | | |
| Field membrane | GAF TPO .060 white, 5'x100' roll (#7561920) | 5,720.0 | SF | 12 | $380.00 | $4,560 | Field roof area + 10% waste ÷ 500 SF/roll |
| *(remaining sections not captured)* | | | | | | | |

The 187 SQ insulation figure and the 5,720 SF membrane figure look inconsistent. Check the Assumptions tab for the roof area actually used.

### 3. Price Book (A1:H36), reusable across jobs
Columns: **Item Description | SKU / Item # | Unit | Coverage / Pack Qty | Unit Cost ($) | Waste % | Basis | Notes**

`Basis` drives the quantity formula: `Field SF`, `Wall Flashing LF`, `Flat / Per Job`, `Manual only`.

| Item | SKU | Unit | Coverage | Unit Cost | Waste | Basis | Notes |
|---|---|---|---|---|---|---|---|
| GAF TPO .060 White 5'x100' | #7561920 | Roll | 500 SF | $380.00 | 10% | Field SF | inv 3/30/26 (also 2/5/26) |
| GAF TPO #1121 Solvent Bond Adh 5 gal | #77800OM | Pail | 300 SF | $170.00 | 5% | Field SF | inv 3/30/26; was $173.56 on 2/4/26; HAZMAT |
| GAF TPO Seam Cleaner 1 gal | 7793 | Can | 1 | $36.65 | 0% | Flat / Per Job | inv 3/30/26; HAZMAT |
| GAF TPO T-Joint Patch White 4"x4" (100/ctn) | #7712920 | EA | 1 | $0.82 | 0% | Manual only | count from field layout |
| GAF TPO UN-55 Detail Memb. Wht 24"x50' | #7624920TP | Roll | 50 LF | $360.00 | 10% | Wall Flashing LF | inv 3/30/26; was $366.82 on 2/4/26 |

Prices come from Marc's GulfEagle invoices (screenshot 9/2/2026). Update them from new invoices before reuse.

## Patterns worth copying into the agent
- Separate **Qty Needed** (net) from **Order Qty** (rounded up to package units).
- Every line carries a **Basis / Notes** formula string, so anyone can audit the math.
- Open items are flagged visually (yellow), and inputs are separated from calculations.
- Sub-quotes (tapered insulation) are carried as a lump sum with the quote number and expiry date.
