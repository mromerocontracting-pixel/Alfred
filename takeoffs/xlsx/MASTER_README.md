# Master Takeoff & Cost Builder

`MASTER_Takeoff_Cost_Builder.xlsx` is the one workbook for every job. It replaces the six per-system templates that used to be in `templates/` and the old `tools/build_cost_builder.py`.

| Tab | What it's for |
|---|---|
| Start Here | Step-by-step instructions |
| Inputs | Pick the **system** (dropdown). Then job info, permitting data (blank cells are counted as missing), measurements, waste %, tax |
| Takeoff | Lines load from the chosen system. Exclude a line (Include = N), add an item in a blank row, or adjust basis, multiplier, waste, manual qty or unit cost. Below the lines: other job costs (no sales tax) and the grand total |
| Price Book | 172 items, each with a **Status** to filter on (PRICE NEEDED, COVERAGE NEEDED, PRICE OLD, CONFIRM, OK) and a count at the top: the full 11/17/2026 shop price list plus the Gulfeagle invoices/quotes and job prices, each with supplier, price date, source and previous price. Yellow = no price yet. Orange = price older than 180 days |
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
This keeps your Price Book, Assemblies, Price Log and Job History. **Don't use `--fresh`**: it resets everything to the old seed list in the script and drops the shop list and every later price.

## Price sources
- `reference/price_lists/2026-11-17_Shop_Price_List.pdf`: where the price has two columns, the right-hand price is entered as current and the SHOP price is kept in Prev. Cost. The pack/pallet counts from the list, like "(25)", are in the Notes column.
- Gulfeagle invoices 2/4, 2/5 and 3/30/26, and quote S002031839 (12/12/24, expired).
- Prices Marc gave on jobs (9795 SW 170th St).

## Check
- **9795 SW 170th St:** at the old prices the master matched Rev 0 exactly ($5,813.22). Rev 1 (`2026-11-20_9795_SW_170th_St_BUR_Takeoff_Rev1.xlsx`) is built from the master at the 11/17/26 shop prices: $5,845.00 material / $6,920.00 grand total.
- **769 NE 74th St** measurements: 7 TPO rolls, 11 pails #1121, 9 boxes anchors, the same as Rev 2.
