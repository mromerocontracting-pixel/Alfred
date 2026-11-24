# Master Takeoff & Cost Builder

`MASTER_Takeoff_Cost_Builder.xlsx` is the one workbook for every job. It replaces the six per-system templates that used to be in `templates/`.

| Tab | What it's for |
|---|---|
| Start Here | Step-by-step instructions |
| Inputs | Pick the **system** (dropdown). Then job info, permitting data (blank cells are counted as missing), measurements, waste %, tax |
| Takeoff | Lines load from the chosen system. Exclude a line (Include = N), add an item in a blank row, or adjust basis, multiplier, waste, manual qty or unit cost. Below the lines: other job costs (no sales tax) and the grand total |
| Price Book | 71 items with supplier, price date, source and previous price. Yellow = no price yet. Orange = price older than 180 days |
| Assemblies | The systems and the lines each one loads. Add your own |
| Price Log | One row per price change |
| Job History | Past takeoffs with $/SQ, as a sanity check |

**Systems included:** TPO fully adhered, TPO mechanically attached, hot-mop BUR (open eave), hot-mop BUR (parapets), mod-bit hot mop, low-slope SA 2-ply, tile + T1, tile + T2, blank.

## New job
1. Open the master and **Save As** `takeoffs/xlsx/YYYY-MM-DD_<job>_Takeoff_Rev0.xlsx`.
2. On Inputs, pick the system, then fill in the measurements and permitting data.
3. On Takeoff, adjust the lines and enter the job costs. Check the Flag column.

## New prices
Change prices **in the master** so every future job picks them up:
1. Move the old cost and date into Prev. Cost / Prev. Date.
2. Type the new cost, date and source.
3. Add a row to the Price Log.

## Rebuilding the layout
```bash
python3 tools/build_master_takeoff.py
```
This keeps your Price Book, Assemblies, Price Log and Job History. `--fresh` resets them to the seed lists in the script.

## Check
- **9795 SW 170th St:** $5,813.22 material / $6,888.22 grand total, the same as Rev 0.
- **769 NE 74th St** measurements: 7 TPO rolls, 11 pails #1121, 9 boxes anchors, the same as Rev 2.
