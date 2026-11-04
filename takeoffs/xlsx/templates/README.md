# Material Quantity & Cost Builder

Excel workbooks with live formulas. Each file starts with a different system's line items already loaded. Built by `tools/build_cost_builder.py`.

| File | Starter system |
|---|---|
| `Cost_Builder_tpo-fa.xlsx` | TPO fully adhered (F3) over tapered ISO, concrete deck |
| `Cost_Builder_tpo-ma.xlsx` | TPO mechanically attached (F3), wood deck |
| `Cost_Builder_modbit-hot.xlsx` | Mod-bit hot mop (F1) over tapered ISO, primed concrete |
| `Cost_Builder_sa-lowslope.xlsx` | Low-slope SA two-ply (L2) |
| `Cost_Builder_tile-t2.xlsx` | Tile (C1/C2) + T2 underlayment |
| `Cost_Builder_blank.xlsx` | Empty takeoff |

## How to use
1. Copy the template to `takeoffs/xlsx/YYYY-MM-DD_<job>_Takeoff_Rev0.xlsx`.
2. **Inputs** tab: fill in the job info, the permitting data, the waste %, and the measurements (Field SF, wall LF, flashing height, LF counts, penetrations). Yellow cells are still blank. The Takeoff tab shows how many permitting items are missing.
3. **Takeoff** tab: pick a **Code** from the dropdown. Product, unit, coverage, and cost are looked up from the Price Book. Then:
   - **Basis Override** sends the line to a different measurement. For example, `Field + Wall SF` puts field and wall membrane on one line so it rounds up once.
   - **Multiplier** sets the number of rows, layers, or plies (term bar rows, anchor rows, mopped layers).
   - **Waste Override**, **Manual Order Qty**, and **Unit Cost Override** (use this for quote prices) replace the lookup on that line only.
   - Order Qty = ROUNDUP(Net × Multiplier × (1 + Waste) ÷ Coverage).
4. The **Flag** column shows `PRICE NEEDED`, `ENTER MEASUREMENT`, `ENTER MANUAL QTY`, or `UNKNOWN CODE`. The total includes priced lines only.

## Updating prices
Edit `PRICE_BOOK` in `tools/build_cost_builder.py` (cite the invoice and date), then run:

```bash
python3 tools/build_cost_builder.py
```

To add an item for a single job, type it into a spare row on that workbook's Price Book tab.

## Check
On the 769 NE 74th Rev 2 measurements (2,439.86 SF field, 262.45 LF wall, 2.5' strips), the builder gives 7 TPO rolls, 11 pails of #1121, 9 boxes of anchors, and 29 pcs of stucco stop. Rev 2 has the same numbers. Term bar comes out at 58 pcs; Marc ordered 60.
