#!/usr/bin/env python3
"""Material Quantity & Cost Builder — generates a live-formula Excel workbook.

Tabs:
  Inputs      job info, permitting data, measurements (the "basis" quantities), tax
  Price Book  every item with SKU, order unit, coverage per unit, cost, waste, basis
  Takeoff     line items: pick a Code, everything else is looked up and calculated
  Assemblies  starter line sets per system (what each --system preloads)

Usage:
  python3 tools/build_cost_builder.py                 # writes every starter template
  python3 tools/build_cost_builder.py --system tpo-fa --out path.xlsx

Edit PRICE_BOOK below when invoices change, then re-run. Prices are from
Gulfeagle invoices / quotes and the shop price list, as cited per row.
"""
import argparse
import os

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

BLUE = Font(color="0000CC")
BOLD = Font(bold=True)
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF")
SEC_FILL = PatternFill("solid", fgColor="D9E1F2")
YELLOW = PatternFill("solid", fgColor="FFF2CC")
RED_FONT = Font(bold=True, color="C00000")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
MONEY = '"$"#,##0.00'
PCT = "0%"
NUM = "#,##0.00"

# ---------------------------------------------------------------------------
# Basis quantities (Inputs tab). name, kind ('in' = typed, or a formula using
# {r:<name>} for another basis row), unit, note.
# ---------------------------------------------------------------------------
BASIS = [
    ("Field SF", "in", "SF", "Roof area from drip-edge polygons / Bluebeam. Never floor area."),
    ("Wall Flashing LF", "in", "LF", "Parapet / wall base length (inside face)."),
    ("Flashing Height FT", "in", "FT", "Base flashing height incl. laps (e.g. 8\" min + lap = 2.5 ft for 30\" strips)."),
    ("Wall Flashing SF", "={r:Wall Flashing LF}*{r:Flashing Height FT}", "SF", "Calculated: LF x height."),
    ("Field + Wall SF", "={r:Field SF}+{r:Wall Flashing SF}", "SF", "Calculated: field + wall flashing. Use for one combined membrane / adhesive / primer line (rounds once, avoids over-ordering)."),
    ("Drip Edge LF", "in", "LF", "Eaves + rakes with edge metal."),
    ("L-Flashing LF", "in", "LF", "Roof-to-wall / L-flashing."),
    ("Hip & Ridge LF", "in", "LF", ""),
    ("Valley LF", "in", "LF", ""),
    ("Rake LF", "in", "LF", ""),
    ("Eave LF", "in", "LF", ""),
    ("Coping LF", "in", "LF", "Parapet top centerline (nailer / coping)."),
    ("Pipe Boots 1-2in EA", "in", "EA", "Count from plumbing riser / roof plan."),
    ("Pipe Boots 3-5in EA", "in", "EA", ""),
    ("Scuppers EA", "in", "EA", "Primary + overflow."),
    ("Drains EA", "in", "EA", ""),
    ("Per Job", "=1", "JOB", "Fixed 1 — for job-level items (seam cleaner, tools)."),
    ("Manual", "=0", "-", "No formula — type the order qty in the Manual Order Qty column."),
]

# ---------------------------------------------------------------------------
# Price book. waste may be a number or "Job" (= Inputs field waste %).
# cost None = price needed. coverage None = coverage unknown (manual qty).
# ---------------------------------------------------------------------------
PB_COLS = ["Code", "Item", "Product / SKU", "Order Unit", "Coverage / Unit", "Cov. Unit",
           "Unit Cost ($)", "Default Waste", "Default Basis", "Price Source / Date", "Notes / Status"]
PRICE_BOOK = [
    # --- TPO (F3, draft preset) ---
    ("TPO-060", "TPO membrane .060 white 5'x100'", "GAF EverGuard TPO #7561920", "Roll", 500, "SF", 380.00, 0.10, "Field SF", "Gulfeagle inv 3/30/26", "F3 draft; NOA TBD. 500 SF gross/roll."),
    ("TPO-060-WALL", "TPO membrane — wall flashing strips", "GAF EverGuard TPO #7561920", "Roll", 500, "SF", 380.00, 0.10, "Wall Flashing SF", "Gulfeagle inv 3/30/26", "Reinforced strips per GAF 301A."),
    ("TPO-UN55", "TPO detail membrane UN-55 24\"x50'", "GAF #7624920TP", "Roll", 50, "LF", 360.00, 0.10, "Manual", "Gulfeagle inv 3/30/26", "Corners / details. Unreinforced."),
    ("TPO-1121", "TPO bonding adhesive 5 gal (field)", "GAF #1121 solvent #77800OM", "Pail", 300, "SF", 170.00, 0.05, "Field SF", "Gulfeagle inv 3/30/26", "Fully adhered only. HAZMAT. Coverage per Solano Prado price book — confirm vs GAF data sheet."),
    ("TPO-1121-WALL", "TPO bonding adhesive 5 gal (walls)", "GAF #1121 solvent #77800OM", "Pail", 300, "SF", 170.00, 0.05, "Wall Flashing SF", "Gulfeagle inv 3/30/26", "HAZMAT."),
    ("TPO-CLEAN", "TPO seam cleaner 1 gal", "GAF #7793", "Can", 1, "JOB", 36.65, 0, "Per Job", "Gulfeagle inv 3/30/26", "HAZMAT."),
    ("TPO-TJOINT", "TPO T-joint patch 4\"x4\"", "GAF #7712920", "EA", 1, "EA", 0.82, 0, "Manual", "Gulfeagle inv 3/30/26", "Count from field layout."),
    ("TPO-BOOT-2", "TPO split pipe boot 1\"-2\" white", "GAF #85G1920", "EA", 1, "EA", 38.51, 0, "Pipe Boots 1-2in EA", "Gulfeagle inv 2/4/26", ""),
    ("TPO-BOOT-5", "TPO split pipe boot 3\"-5\" white", "GAF #85G2920", "EA", 1, "EA", 45.45, 0, "Pipe Boots 3-5in EA", "Gulfeagle quote S002031839 12/12/24", "Quote expired — reconfirm."),
    ("TPO-SCUP", "TPO scupper 8x10x12 white", "GAF EverGuard #B5TB920", "EA", 1, "EA", 212.75, 0, "Scuppers EA", "Gulfeagle quote S002031839 12/12/24", "Quote expired — reconfirm."),
    ("TPO-WBLOCK", "Water Block 10.3 oz", "GAF EverGuard #8008", "Tube", None, "", 8.50, 0, "Manual", "769 NE 74th Rev 2", "Coverage unknown — manual qty."),
    ("TPO-FLEX", "FlexSeal caulk-grade sealant", "GAF TopCoat FlexSeal #8962920WP", "Tube", None, "", 14.00, 0, "Manual", "769 NE 74th Rev 2", "Coverage unknown — manual qty."),
    ("TPO-FAST", "TPO plate fasteners (mech. attached)", "Drill-Tec #14 + 2-3/4\" barbed plates", "EA", 1, "EA", None, 0, "Manual", "", "Count from NOA row spacing (e.g. 25-0707.01 E(4)). PRICE NEEDED."),
    # --- Mod-bit / BUR (F1 / L4) ---
    ("MB-PRIMER", "Asphalt primer 5 gal", "Tropical 410", "Pail", 500, "SF", 43.48, 0, "Field + Wall SF", "Shop list 6/26/26", "~100 SF/gal (ASTM D41 typ.) — confirm coverage."),
    ("MB-STRATAVENT", "Venting base sheet", "GAF StrataVent", "Roll", None, "SF", 59.00, 0.10, "Field SF", "Shop list 6/26/26", "Roll coverage not in price book — manual qty."),
    ("MB-RUB20", "Smooth ply / base flashing ply 1.5 SQ", "GAF Ruberoid 20 smooth", "Roll", 150, "SF", 85.00, 0.10, "Field SF", "Shop list 6/26/26", ""),
    ("MB-RUB20-WALL", "Smooth ply — wall flashing", "GAF Ruberoid 20 smooth", "Roll", 150, "SF", 85.00, 0.10, "Wall Flashing SF", "Shop list 6/26/26", ""),
    ("MB-CAP", "Granulated cap sheet 1.25 SQ", "GAF Capsheet (granulated)", "Roll", 125, "SF", 59.90, 0.10, "Field SF", "Shop list 6/26/26", "Confirm product (Ruberoid / mineral cap)."),
    ("MB-CAP-WALL", "Granulated cap — wall flashing", "GAF Capsheet (granulated)", "Roll", 125, "SF", 59.90, 0.10, "Wall Flashing SF", "Shop list 6/26/26", ""),
    ("MB-ASPHALT", "Hot asphalt Type III, 100-lb keg", "Asphalt (price book 'Asphalt (24)')", "Keg", 400, "SF", 40.00, 0.10, "Field SF", "Shop list 6/26/26", "25 lb/SQ per mopped layer -> 400 SF/keg. Set Multiplier = mopped layers. Confirm unit."),
    ("MB-CANT", "Cant strip 1x4", "Cant strip (84 LF/unit)", "EA", 84, "LF", 40.00, 0.10, "Wall Flashing LF", "Shop list 6/26/26", "Confirm unit."),
    ("MB-FLCEM", "Flashing cement (term bar seal)", "Tropical 2100", "Tube", 12, "LF", 6.15, 0.10, "Wall Flashing LF", "Shop list 6/26/26", "12 LF/tube."),
    ("MB-GRAN", "Granules (touch-up)", "Granule bag", "Bag", 1, "JOB", 19.80, 0, "Manual", "Shop list 6/26/26", ""),
    # --- Edge / wall metal, anchors, sealant (any low-slope) ---
    ("TERMBAR", "Termination bar 10'", "OMG flat alum #FLATB06", "PC", 10, "LF", 8.00, 0.10, "Wall Flashing LF", "Price book", "Multiplier = rows of term bar."),
    ("ANCHOR", "Masonry anchors 1/4\"x1-1/4\" (100/box)", "OMG #MA114X", "Box", 100, "EA", 9.00, 0.10, "Wall Flashing LF", "Price book", "1 per LF @ 12\" o.c. Multiplier = rows (term bar + counterflashing)."),
    ("STUCCOSTOP", "Counterflashing stucco stop 5\" 26 ga 10'", "Stucco stop galv", "PC", 10, "LF", 8.15, 0.10, "Wall Flashing LF", "Price book", "Alt: 2-part SS reglet — price TBD."),
    ("SEAL-915", "Sealant (top of counterflashing)", "Bostik 915 white", "Tube", 12, "LF", 4.90, 0.10, "Wall Flashing LF", "Shop list 6/26/26", "12 LF/tube."),
    ("NAILER-2X8", "Wood nailer 2x8x10", "2x8x10 (confirm PT / width)", "EA", 10, "LF", 10.85, 0.10, "Coping LF", "Shop list 6/26/26", "Confirm pressure-treated."),
    ("DRIPEDGE", "Drip edge (A1)", "Gauge / metal TBD", "PC", 10, "LF", None, 0.10, "Drip Edge LF", "", "A1 draft. PRICE NEEDED."),
    ("COPING", "Metal coping cap + cleat", "Gauge / finish TBD", "LF", 1, "LF", None, 0.10, "Coping LF", "", "Sheet-metal quote needed."),
    # --- Insulation (L5 / A6) ---
    ("ISO-TAPER-LS", "Tapered ISO system (supplier quote)", "Gulfeagle tapered quote #", "LS", 1, "JOB", None, 0, "Per Job", "", "Enter quote $ in Unit Cost Override + quote # and expiry in Notes."),
    ("ISO-ADH", "Insulation adhesive", "OlyBond 500", "EA", None, "", 1080.00, 0, "Manual", "769 NE 74th Rev 1 (Marc)", "Coverage per NOA — manual qty."),
    # --- Tile & metal underlayments (handoff presets) ---
    ("T-TILESEAL", "TileSeal (T1 / T2 top)", "Westlake TileSeal", "Roll", 200, "SF", None, "Job", "Field SF", "", "2.0 SQ net/roll (laps incl.). Open Item 2: roll size. PRICE NEEDED."),
    ("T-CITADEL", "Citadel PRO base (T2)", "Westlake Citadel PRO FL14317", "Roll", 200, "SF", None, "Job", "Field SF", "", "2.0 SQ net/roll. PRICE NEEDED."),
    ("T-FLSACAP", "Flintlastic SA Cap (T3)", "CertainTeed Flintlastic SA Cap", "Roll", 100, "SF", None, "Job", "Field SF", "", "1.0 SQ net/roll. Open Item 1 (T3). PRICE NEEDED."),
    ("UM-XFR", "Polystick XFR (U-M1)", "Polyglass Polystick XFR", "Roll", 150, "SF", None, "Job", "Field SF", "", "1.5 SQ net, 3\" side / 6\" end laps, 265F. PRICE NEEDED."),
    # --- Low-slope SA assemblies (L1-L3) ---
    ("L-ELASTOBASE", "Elastobase base, mech. attached (L1)", "Polyglass Elastobase", "Roll", 200, "SF", None, 0.10, "Field SF", "", "2.0 SQ. Tin tags / caps per NOA row spacing. PRICE NEEDED."),
    ("L-SAV", "Elastoflex SA V base (L2)", "Polyglass Elastoflex SA V", "Roll", 200, "SF", None, 0.10, "Field + Wall SF", "", "2.0 SQ. PRICE NEEDED."),
    ("L-SAP", "Elastoflex SA P cap (L1/L2)", "Polyglass Elastoflex SA P", "Roll", 100, "SF", None, 0.10, "Field + Wall SF", "", "1.0 SQ. Open Item 3 (SA P vs Polyflex). PRICE NEEDED."),
    ("L-NAILBASE", "Flintlastic SA NailBase / PlyBase (L3)", "CertainTeed Flintlastic SA NailBase", "Roll", 200, "SF", None, 0.10, "Field SF", "", "2.0 SQ. PRICE NEEDED."),
    ("L-FLCAP", "Flintlastic SA Cap (L3 cap)", "CertainTeed Flintlastic SA Cap", "Roll", 100, "SF", None, 0.10, "Field + Wall SF", "", "1.0 SQ. PRICE NEEDED."),
    # --- Tile covering placeholders (C1-C3) ---
    ("TILE-FIELD", "Field tile", "Manufacturer / profile TBD", "SQ", 100, "SF", None, "Job", "Field SF", "", "Pcs/SQ from manufacturer sheet — never assumed. Add tile/metal cut buffer to waste. PRICE NEEDED."),
    ("TILE-HR", "Hip & ridge tile", "Manufacturer TBD", "PC", None, "LF", None, 0.10, "Hip & Ridge LF", "", "Pcs/LF from manufacturer sheet. PRICE NEEDED."),
    ("TILE-ADH", "Tile adhesive (foam paddies)", "Per NOA attachment table", "Kit", None, "", None, 0.05, "Manual", "", "Per NOA attachment table. PRICE NEEDED."),
    ("VALLEY-MTL", "Valley metal", "Gauge / metal TBD", "PC", 10, "LF", None, 0.10, "Valley LF", "", "PRICE NEEDED."),
    # --- Tools / consumables ---
    ("TOOL-BRUSH", "Brush 4\"", "Brush 4", "EA", 1, "EA", 1.47, 0, "Manual", "Shop list 6/26/26", ""),
    ("TOOL-BIT", "Masonry drill bit", "Drill bits", "EA", 1, "EA", 2.64, 0, "Manual", "Shop list 6/26/26", ""),
    ("TOOL-RFRAME", "Roller frame 9\" HD", "C&R #RF9HDN1", "EA", 1, "EA", 2.70, 0, "Manual", "Gulfeagle inv 2/5/26", ""),
    ("TOOL-RCOVER", "Roller cover 9\" 3/4\" nap", "C&R #RC9-3/4", "EA", 1, "EA", 1.65, 0, "Manual", "Gulfeagle inv 2/5/26", ""),
    ("TOOL-MOP", "Mop", "Mop", "EA", 1, "EA", 7.15, 0, "Manual", "Shop list 6/26/26", ""),
]

# Starter line sets: (code, basis override or None, multiplier, manual qty or None)
ASSEMBLIES = {
    "blank": ("Blank takeoff", []),
    "tpo-fa": ("TPO fully adhered (F3) over tapered ISO — concrete deck", [
        ("ISO-TAPER-LS", None, 1, None), ("ISO-ADH", None, 1, None),
        ("TPO-060", "Field + Wall SF", 1, None), ("TPO-UN55", None, 1, 1),
        ("TPO-1121", "Field + Wall SF", 1, None), ("TPO-CLEAN", None, 1, None),
        ("TPO-TJOINT", None, 1, None), ("TPO-BOOT-2", None, 1, None), ("TPO-BOOT-5", None, 1, None),
        ("TPO-SCUP", None, 1, None), ("TERMBAR", None, 2, None), ("ANCHOR", None, 3, None),
        ("STUCCOSTOP", None, 1, None), ("TPO-WBLOCK", None, 1, None), ("TPO-FLEX", None, 1, None),
        ("TOOL-BRUSH", None, 1, 6), ("TOOL-BIT", None, 1, 6), ("TOOL-RFRAME", None, 1, 4),
        ("TOOL-RCOVER", None, 1, 12), ("TOOL-MOP", None, 1, 2)]),
    "tpo-ma": ("TPO mechanically attached (F3) — wood deck", [
        ("TPO-060", "Field + Wall SF", 1, None), ("TPO-UN55", None, 1, 1),
        ("TPO-FAST", None, 1, None), ("TPO-1121-WALL", None, 1, None), ("TPO-CLEAN", None, 1, None),
        ("TPO-TJOINT", None, 1, None), ("TPO-BOOT-2", None, 1, None), ("TPO-BOOT-5", None, 1, None),
        ("TERMBAR", None, 1, None), ("NAILER-2X8", None, 1, None), ("COPING", None, 1, None),
        ("DRIPEDGE", None, 1, None), ("TOOL-BRUSH", None, 1, 6), ("TOOL-RFRAME", None, 1, 4),
        ("TOOL-RCOVER", None, 1, 12)]),
    "modbit-hot": ("Mod-bit hot mop (F1) over tapered ISO — primed concrete", [
        ("MB-PRIMER", None, 1, None), ("ISO-TAPER-LS", None, 1, None), ("MB-STRATAVENT", None, 1, None),
        ("MB-RUB20", None, 1, None), ("MB-RUB20-WALL", None, 1, None), ("MB-CAP", None, 1, None),
        ("MB-CAP-WALL", None, 1, None), ("MB-ASPHALT", None, 3, None), ("MB-CANT", None, 1, None),
        ("TERMBAR", None, 1, None), ("STUCCOSTOP", None, 1, None), ("ANCHOR", None, 2, None),
        ("MB-FLCEM", None, 1, None), ("SEAL-915", None, 1, None), ("MB-GRAN", None, 1, 2),
        ("TOOL-MOP", None, 1, 6), ("TOOL-BRUSH", None, 1, 6)]),
    "sa-lowslope": ("Low-slope SA 2-ply (L2: Elastoflex SA V + SA P)", [
        ("MB-PRIMER", None, 1, None), ("L-SAV", None, 1, None), ("L-SAP", None, 1, None),
        ("DRIPEDGE", None, 1, None), ("TERMBAR", None, 1, None), ("STUCCOSTOP", None, 1, None),
        ("ANCHOR", None, 2, None), ("SEAL-915", None, 1, None), ("TOOL-BRUSH", None, 1, 6)]),
    "tile-t2": ("Tile (C1/C2) + T2 two-ply underlayment", [
        ("T-CITADEL", None, 1, None), ("T-TILESEAL", None, 1, None), ("TILE-FIELD", None, 1, None),
        ("TILE-HR", None, 1, None), ("TILE-ADH", None, 1, None), ("VALLEY-MTL", None, 1, None),
        ("DRIPEDGE", None, 1, None)]),
}

TAKEOFF_ROWS = 60  # editable line slots
FIRST = 6           # first line row on Takeoff


def header(ws, row, labels, widths=None):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font, c.fill, c.alignment, c.border = HDR_FONT, HDR_FILL, Alignment(wrap_text=True, vertical="center"), BOX
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def build(system, out):
    title, lines = ASSEMBLIES[system]
    wb = Workbook()

    # ---------------- Inputs ----------------
    ws = wb.active
    ws.title = "Inputs"
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 70
    ws["A1"] = "MATERIAL QUANTITY & COST BUILDER — M. Romero's Roofing & Inspections, Inc."
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = f"Starter: {title}.  Blue = input.  Yellow = missing / confirm before ordering."
    ws["A2"].font = Font(italic=True)

    r = 4
    ws.cell(row=r, column=1, value="JOB").font = BOLD
    ws.cell(row=r, column=1).fill = SEC_FILL
    job_fields = [("Job name / address", ""), ("Date", ""), ("Revision", "Rev 0"), ("System / preset IDs", title),
                  ("Plan set / report", ""), ("Prepared by", "")]
    for lab, val in job_fields:
        r += 1
        ws.cell(row=r, column=1, value=lab)
        c = ws.cell(row=r, column=2, value=val or None)
        c.font = BLUE
    ws.merge_cells(start_row=r - len(job_fields) + 1, start_column=2, end_row=r - len(job_fields) + 1, end_column=4)

    r += 2
    ws.cell(row=r, column=1, value="CRITICAL MISSING DATA FOR MIAMI-DADE PERMITTING").font = BOLD
    ws.cell(row=r, column=1).fill = SEC_FILL
    crit_start = r + 1
    for lab in ["Roof slope / pitch", "Mean roof height (ft)", "Risk Category", "Exposure Category",
                "Zone 1 pressure (psf)", "Zone 2 pressure (psf)", "Zone 3 pressure (psf)",
                "Deck type & condition", "New / re-roof (layers to remove)", "Covering NOA / FL#",
                "Underlayment / base NOA / FL#", "Insulation NOA / FL#"]:
        r += 1
        ws.cell(row=r, column=1, value=lab)
        ws.cell(row=r, column=2).font = BLUE
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
    crit_end = r
    ws.conditional_formatting.add(f"B{crit_start}:B{crit_end}",
                                  FormulaRule(formula=[f'LEN(B{crit_start})=0'], fill=YELLOW))
    r += 1
    ws.cell(row=r, column=1, value="Missing permitting items")
    ws.cell(row=r, column=2, value=f'=COUNTBLANK(B{crit_start}:B{crit_end})').font = RED_FONT
    missing_cell = f"Inputs!$B${r}"

    r += 2
    ws.cell(row=r, column=1, value="WASTE & TAX").font = BOLD
    ws.cell(row=r, column=1).fill = SEC_FILL
    r += 1
    ws.cell(row=r, column=1, value="Field waste % (items set to 'Job')")
    c = ws.cell(row=r, column=2, value=0.15 if system == "tile-t2" else 0.10)
    c.font, c.number_format, c.fill = BLUE, PCT, YELLOW
    ws.cell(row=r, column=4, value="10% gable · 15% hip · 18-22% cut-up. Add 5-10% cut buffer for tile/metal. Net roll coverage already includes laps.")
    wb.defined_names["JobWaste"] = DefinedName("JobWaste", attr_text=f"Inputs!$B${r}")
    r += 1
    ws.cell(row=r, column=1, value="Sales tax rate")
    c = ws.cell(row=r, column=2, value=0.07)
    c.font, c.number_format = BLUE, PCT
    wb.defined_names["TaxRate"] = DefinedName("TaxRate", attr_text=f"Inputs!$B${r}")

    r += 2
    ws.cell(row=r, column=1, value="MEASUREMENTS (basis quantities)").font = BOLD
    ws.cell(row=r, column=1).fill = SEC_FILL
    r += 1
    for i, lab in enumerate(["Basis", "Value", "Unit", "Source / Note"], 1):
        c = ws.cell(row=r, column=i, value=lab)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
    basis_rows = {}
    start = r + 1
    for name, *_ in BASIS:
        r += 1
        basis_rows[name] = r
    r = start - 1
    for name, kind, unit, note in BASIS:
        r += 1
        ws.cell(row=r, column=1, value=name).border = BOX
        if kind == "in":
            c = ws.cell(row=r, column=2, value=None)
            c.font = BLUE
        else:
            f = kind
            for n, rr in basis_rows.items():
                f = f.replace("{r:" + n + "}", f"B{rr}")
            c = ws.cell(row=r, column=2, value=f)
        c.number_format, c.border = NUM, BOX
        ws.cell(row=r, column=3, value=unit).border = BOX
        ws.cell(row=r, column=4, value=note).border = BOX
    end = r
    wb.defined_names["BasisNames"] = DefinedName("BasisNames", attr_text=f"Inputs!$A${start}:$A${end}")
    wb.defined_names["BasisValues"] = DefinedName("BasisValues", attr_text=f"Inputs!$B${start}:$B${end}")
    r += 1
    ws.cell(row=r, column=1, value="Field SQ (calculated)")
    ws.cell(row=r, column=2, value=f"=B{basis_rows['Field SF']}/100").number_format = NUM
    ws.cell(row=r, column=3, value="SQ")
    fsf = basis_rows["Field SF"]
    ws.conditional_formatting.add(f"B{fsf}", FormulaRule(formula=[f"LEN(B{fsf})=0"], fill=YELLOW))

    # ---------------- Price Book ----------------
    pb = wb.create_sheet("Price Book")
    pb["A1"] = "PRICE BOOK — update from new invoices before reuse. Blank Unit Cost = PRICE NEEDED. Blank coverage = manual qty."
    pb["A1"].font = BOLD
    header(pb, 3, PB_COLS, [16, 38, 34, 9, 10, 8, 11, 10, 20, 30, 60])
    for i, row in enumerate(PRICE_BOOK):
        rr = 4 + i
        for j, v in enumerate(row, 1):
            c = pb.cell(row=rr, column=j, value=v)
            c.border, c.alignment = BOX, WRAP
            if j in (5, 7, 8):
                c.font = BLUE
        pb.cell(row=rr, column=7).number_format = MONEY
        pb.cell(row=rr, column=8).number_format = PCT
        if row[6] is None:
            pb.cell(row=rr, column=7).fill = YELLOW
        if row[4] is None:
            pb.cell(row=rr, column=5).fill = YELLOW
    pb_end = 3 + len(PRICE_BOOK) + 40  # spare rows for new items
    for col, nm in [("A", "PB_Code"), ("B", "PB_Item"), ("C", "PB_Product"), ("D", "PB_Unit"),
                    ("E", "PB_Cov"), ("G", "PB_Cost"), ("H", "PB_Waste"), ("I", "PB_Basis"), ("K", "PB_Notes")]:
        wb.defined_names[nm] = DefinedName(nm, attr_text=f"'Price Book'!${col}$4:${col}${pb_end}")
    dv_b = DataValidation(type="list", formula1="=BasisNames", allow_blank=True)
    pb.add_data_validation(dv_b)
    dv_b.add(f"I4:I{pb_end}")
    pb.freeze_panes = "B4"

    # ---------------- Takeoff ----------------
    tk = wb.create_sheet("Takeoff", 1)
    cols = ["Code", "Item", "Product / SKU", "Basis Override", "Basis Used", "Multiplier (rows / layers)",
            "Net Qty", "Waste Override", "Waste Used", "Gross Qty", "Coverage / Unit", "Calc Order Qty",
            "Manual Order Qty", "Order Qty", "Unit", "Unit Cost Override", "Unit Cost", "Ext. Cost",
            "Flag", "Notes / Source"]
    tk["A1"] = "=\"MATERIAL TAKEOFF — \"&IF(LEN(Inputs!B5)=0,\"(job name)\",Inputs!B5)&\" — \"&Inputs!B7"
    tk["A1"].font = Font(bold=True, size=13)
    tk["A2"] = f"System: {title}. Type a Code (dropdown); blue columns are inputs. Order Qty = ROUNDUP(Net x Multiplier x (1+Waste) / Coverage) unless a Manual Order Qty is typed."
    tk["A2"].font = Font(italic=True)
    tk["A3"] = f'=IF({missing_cell}>0,"⚠ "&{missing_cell}&" permitting item(s) missing on Inputs — see Critical Missing Data. Confirm NOAs before ordering.","Permitting data entered — confirm every NOA / FL# against the job before ordering.")'
    tk["A3"].font = RED_FONT
    header(tk, 5, cols, [15, 30, 28, 16, 16, 10, 10, 9, 8, 10, 9, 9, 9, 9, 7, 10, 10, 12, 16, 34])
    tk.row_dimensions[5].height = 42
    last = FIRST + TAKEOFF_ROWS - 1
    for rr in range(FIRST, last + 1):
        A = f"$A{rr}"
        lk = lambda nm: f'IFERROR(INDEX({nm},MATCH({A},PB_Code,0)),"")'
        f = {
            "B": f'=IF({A}="","",{lk("PB_Item")})',
            "C": f'=IF({A}="","",{lk("PB_Product")})',
            "E": f'=IF({A}="","",IF(D{rr}<>"",D{rr},{lk("PB_Basis")}))',
            "G": f'=IF(OR({A}="",E{rr}=""),"",IFERROR(INDEX(BasisValues,MATCH(E{rr},BasisNames,0)),0)*IF(F{rr}="",1,F{rr}))',
            "I": f'=IF({A}="","",IF(H{rr}<>"",H{rr},IF({lk("PB_Waste")}="Job",JobWaste,N({lk("PB_Waste")}))))',
            "J": f'=IF(G{rr}="","",G{rr}*(1+I{rr}))',
            "K": f'=IF({A}="","",{lk("PB_Cov")})',
            "L": f'=IF(OR(J{rr}="",K{rr}="",N(K{rr})=0),0,ROUNDUP(J{rr}/K{rr},0))',
            "N": f'=IF({A}="","",IF(M{rr}<>"",M{rr},L{rr}))',
            "O": f'=IF({A}="","",{lk("PB_Unit")})',
            "Q": f'=IF({A}="","",IF(P{rr}<>"",P{rr},{lk("PB_Cost")}))',
            "R": f'=IF(OR({A}="",Q{rr}=""),0,N(N{rr})*Q{rr})',
            "S": (f'=IF({A}="","",IF(ISNA(MATCH({A},PB_Code,0)),"UNKNOWN CODE",'
                  f'IF(Q{rr}="","PRICE NEEDED",IF(AND(N(N{rr})=0,M{rr}=""),'
                  f'IF(OR(E{rr}="Manual",K{rr}="",N(K{rr})=0),"ENTER MANUAL QTY","ENTER MEASUREMENT"),""))))'),
        }
        for col, formula in f.items():
            tk[f"{col}{rr}"] = formula
        for ci in range(1, 21):
            c = tk.cell(row=rr, column=ci)
            c.border = BOX
            if get_column_letter(ci) in "ADFHMPT":
                c.font = BLUE
        for col in "GJ":
            tk[f"{col}{rr}"].number_format = NUM
        for col in "HI":
            tk[f"{col}{rr}"].number_format = PCT
        for col in "PQR":
            tk[f"{col}{rr}"].number_format = MONEY
        tk[f"S{rr}"].font = RED_FONT
    for i, (code, bo, mult, manual) in enumerate(lines):
        rr = FIRST + i
        tk[f"A{rr}"] = code
        if bo:
            tk[f"D{rr}"] = bo
        tk[f"F{rr}"] = mult
        if manual is not None:
            tk[f"M{rr}"] = manual
    for rr in range(FIRST + len(lines), last + 1):
        tk[f"F{rr}"] = 1
    dv_code = DataValidation(type="list", formula1="=PB_Code", allow_blank=True)
    dv_basis = DataValidation(type="list", formula1="=BasisNames", allow_blank=True)
    tk.add_data_validation(dv_code)
    tk.add_data_validation(dv_basis)
    dv_code.add(f"A{FIRST}:A{last}")
    dv_basis.add(f"D{FIRST}:D{last}")
    tk.conditional_formatting.add(f"A{FIRST}:T{last}",
                                  FormulaRule(formula=[f'LEN($S{FIRST})>0'], fill=YELLOW))
    t = last + 2
    tk[f"Q{t}"] = "Material subtotal"
    tk[f"R{t}"] = f"=SUM(R{FIRST}:R{last})"
    tk[f"Q{t+1}"] = "=\"Sales tax \"&TEXT(TaxRate,\"0.0%\")"
    tk[f"R{t+1}"] = f"=ROUND(R{t}*TaxRate,2)"
    tk[f"Q{t+2}"] = "TOTAL MATERIAL"
    tk[f"R{t+2}"] = f"=R{t}+R{t+1}"
    tk[f"Q{t+3}"] = "Lines flagged"
    tk[f"R{t+3}"] = f'=COUNTIF(S{FIRST}:S{last},"?*")'
    tk[f"Q{t+4}"] = "Lines needing price"
    tk[f"R{t+4}"] = f'=COUNTIF(S{FIRST}:S{last},"PRICE NEEDED")'
    for k in range(5):
        tk[f"Q{t+k}"].font = BOLD
        tk[f"R{t+k}"].font = BOLD
        tk[f"R{t+k}"].number_format = MONEY if k < 3 else "0"
    tk[f"R{t+2}"].fill = SEC_FILL
    tk[f"A{t}"] = "TOTAL covers priced lines only. Any 'PRICE NEEDED' line is not in the total."
    tk[f"A{t}"].font = RED_FONT
    tk.freeze_panes = f"C{FIRST}"

    # ---------------- Assemblies ----------------
    asm = wb.create_sheet("Assemblies")
    asm["A1"] = "STARTER LINE SETS — regenerate with:  python3 tools/build_cost_builder.py --system <key>"
    asm["A1"].font = BOLD
    header(asm, 3, ["Key", "System", "Codes (multiplier)"], [14, 60, 120])
    for i, (k, (ttl, ls)) in enumerate(ASSEMBLIES.items()):
        asm.cell(row=4 + i, column=1, value=k)
        asm.cell(row=4 + i, column=2, value=ttl)
        asm.cell(row=4 + i, column=3, value=", ".join(f"{c}" + (f" (x{m})" if m != 1 else "") for c, _, m, _ in ls))

    wb.active = 1
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    wb.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--system", choices=list(ASSEMBLIES), help="starter line set (default: all)")
    ap.add_argument("--out", help="output .xlsx (only with --system)")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    tdir = os.path.join(here, "..", "takeoffs", "xlsx", "templates")
    systems = [a.system] if a.system else list(ASSEMBLIES)
    for s in systems:
        out = a.out if (a.out and a.system) else os.path.join(tdir, f"Cost_Builder_{s}.xlsx")
        print(build(s, os.path.normpath(out)))
