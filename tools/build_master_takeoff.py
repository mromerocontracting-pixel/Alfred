#!/usr/bin/env python3
"""MASTER TAKEOFF — one Excel workbook for every job.

  Start Here   how to use it
  Inputs       job info, SYSTEM picker, permitting data, measurements, waste, tax
  Takeoff      lines load from the chosen system; adjust any line; job costs; totals
  Price Book   every item we have priced (supplier, date, source, previous price)
  Assemblies   the line sets each system loads (editable; add your own systems)
  Price Log    record price changes here
  Job History  past takeoffs for a $/SQ sanity check

The Excel file is the source of truth for prices, systems, the price log and job
history. To rebuild the layout without losing any of that, run:
    python3 tools/build_master_takeoff.py            # keeps Price Book, Assemblies, Price Log, Job History
    python3 tools/build_master_takeoff.py --fresh    # DANGER: resets to the old seed lists below (loses the
                                                     # 11/17/26 shop list and every later price)
"""
import argparse
import datetime as dt
import os

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "takeoffs", "xlsx", "MASTER_Takeoff_Cost_Builder.xlsx"))

BLUE = Font(color="0000CC")
BOLD = Font(bold=True)
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF")
SEC_FILL = PatternFill("solid", fgColor="D9E1F2")
YELLOW = PatternFill("solid", fgColor="FFF2CC")
ORANGE = PatternFill("solid", fgColor="F8CBAD")
GREY = PatternFill("solid", fgColor="E7E6E6")
RED_FONT = Font(bold=True, color="C00000")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
MONEY = '"$"#,##0.00'
PCT = "0%"
NUM = "#,##0.00"
DATE = "mm/dd/yy"
STALE_DAYS = 180

D = dt.date
# ---------------------------------------------------------------------------
# Measurements (basis quantities). name, formula or "in", unit, note
# ---------------------------------------------------------------------------
BASIS = [
    ("Field SF", "in", "SF", "Roof area from drip-edge polygons / Bluebeam. Never floor area."),
    ("Wall Flashing LF", "in", "LF", "Parapet / wall base length (inside face)."),
    ("Flashing Height FT", "in", "FT", "Base flashing height incl. laps (8\" min above roof + lap)."),
    ("Wall Flashing SF", "={Wall Flashing LF}*{Flashing Height FT}", "SF", "Calculated: wall LF x height."),
    ("Field + Wall SF", "={Field SF}+{Wall Flashing SF}", "SF", "Calculated. One combined membrane / adhesive / primer line rounds once."),
    ("Drip Edge LF", "in", "LF", "Eaves + rakes with edge metal."),
    ("L-Flashing LF", "in", "LF", "Roof-to-wall / sidewall."),
    ("Hip & Ridge LF", "in", "LF", ""),
    ("Valley LF", "in", "LF", ""),
    ("Rake LF", "in", "LF", ""),
    ("Eave LF", "in", "LF", ""),
    ("Coping LF", "in", "LF", "Parapet top centerline."),
    ("Pipe Boots 1-2in EA", "in", "EA", ""),
    ("Pipe Boots 3-5in EA", "in", "EA", ""),
    ("Pipe Boots 6-8in EA", "in", "EA", ""),
    ("Vents EA", "in", "EA", ""),
    ("Scuppers EA", "in", "EA", "Primary + overflow."),
    ("Drains EA", "in", "EA", ""),
    ("Equipment Legs EA", "in", "EA", "A/C stand legs (pitch pans)."),
    ("Per Job", "=1", "JOB", "Fixed 1 — job-level items."),
    ("Manual", "=0", "-", "Type the qty in Manual Order Qty."),
]

# ---------------------------------------------------------------------------
# Price book seed. waste: number or "Job" (= Inputs field waste). cost None = price needed.
# (code, category, item, product/SKU, supplier, unit, coverage, cov_unit, cost, waste, basis,
#  price_date, source, prev_cost, prev_date, notes)
# ---------------------------------------------------------------------------
GE = "Gulfeagle"
SHOP = "Shop list"
PB = [
    # TPO
    ("TPO-060", "TPO", "TPO membrane .060 white 5'x100'", "GAF EverGuard TPO #7561920", GE, "Roll", 500, "SF", 380.00, 0.10, "Field SF", D(2026, 3, 30), "Gulfeagle inv 3/30/26", None, None, "F3 draft. NOA TBD."),
    ("TPO-060-WALL", "TPO", "TPO membrane — wall flashing strips", "GAF EverGuard TPO #7561920", GE, "Roll", 500, "SF", 380.00, 0.10, "Wall Flashing SF", D(2026, 3, 30), "Gulfeagle inv 3/30/26", None, None, "Reinforced strips per GAF 301A."),
    ("TPO-UN55", "TPO", "TPO detail membrane UN-55 24\"x50'", "GAF #7624920TP", GE, "Roll", 50, "LF", 360.00, 0.10, "Manual", D(2026, 3, 30), "Gulfeagle inv 3/30/26", 376.28, D(2024, 12, 12), "Corners / details. Unreinforced."),
    ("TPO-1121", "TPO", "TPO bonding adhesive 5 gal", "GAF #1121 solvent #77800OM", GE, "Pail", 300, "SF", 170.00, 0.05, "Field SF", D(2026, 3, 30), "Gulfeagle inv 3/30/26", 165.54, D(2024, 12, 12), "Fully adhered. HAZMAT. Coverage per Solano Prado book — confirm vs GAF data."),
    ("TPO-1121-WALL", "TPO", "TPO bonding adhesive 5 gal (walls)", "GAF #1121 solvent #77800OM", GE, "Pail", 300, "SF", 170.00, 0.05, "Wall Flashing SF", D(2026, 3, 30), "Gulfeagle inv 3/30/26", None, None, "HAZMAT."),
    ("TPO-CLEAN", "TPO", "TPO seam cleaner 1 gal", "GAF #7793", GE, "Can", 1, "JOB", 36.65, 0, "Per Job", D(2026, 3, 30), "Gulfeagle inv 3/30/26", 43.62, D(2024, 12, 12), "HAZMAT."),
    ("TPO-TJOINT", "TPO", "TPO T-joint patch 4\"x4\"", "GAF #7712920", GE, "EA", 1, "EA", 0.82, 0, "Manual", D(2026, 3, 30), "Gulfeagle inv 3/30/26", 0.99, D(2024, 12, 12), "Count from field layout (~1 per 60 SF)."),
    ("TPO-BOOT-2", "TPO", "TPO split pipe boot 1\"-2\" white", "GAF #85G1920", GE, "EA", 1, "EA", 38.51, 0, "Pipe Boots 1-2in EA", D(2026, 2, 4), "Gulfeagle inv 2/4/26", 42.93, D(2024, 12, 12), ""),
    ("TPO-BOOT-5", "TPO", "TPO split pipe boot 3\"-5\" white", "GAF #85G2920", GE, "EA", 1, "EA", 45.45, 0, "Pipe Boots 3-5in EA", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Quote expired — reconfirm."),
    ("TPO-BOOT-8", "TPO", "TPO split pipe boot 6\"-8\" white", "GAF #85G3920", GE, "EA", 1, "EA", 9.77, 0, "Pipe Boots 6-8in EA", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Price looks low vs smaller boots — verify."),
    ("TPO-VENTBOOT", "TPO", "TPO vent boot 1\"-6\" white", "GAF #7710920", GE, "EA", 1, "EA", 38.98, 0, "Vents EA", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Quote expired — reconfirm."),
    ("TPO-CONEBOOT", "TPO", "PVC conical pipe boot 1\"-6\" white", "GAF special order (no returns)", GE, "EA", 1, "EA", 36.00, 0, "Manual", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Special order — no returns."),
    ("TPO-SCUP", "TPO", "TPO scupper 8x10x12 white", "GAF EverGuard #B5TB920", GE, "EA", 1, "EA", 212.75, 0, "Scuppers EA", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Quote expired — reconfirm."),
    ("TPO-SCUP-4X6", "TPO", "TPO scupper 4x6x12 white", "GAF EverGuard #B5TA920", GE, "EA", 1, "EA", 156.35, 0, "Manual", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Quote expired — reconfirm."),
    ("TPO-DRAIN-3", "TPO", "TPO Hercules drain 3\"", "GAF special order (no returns)", GE, "EA", 1, "EA", 385.00, 0, "Drains EA", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Special order — no returns."),
    ("TPO-WBLOCK", "TPO", "Water Block mastic 10.3 oz", "GAF EverGuard #8008", GE, "Tube", None, "", 8.50, 0, "Manual", D(2026, 10, 20), "769 NE 74th Rev 2", 7.89, D(2024, 12, 12), "Coverage unknown — manual qty."),
    ("TPO-FLEX", "TPO", "FlexSeal caulk-grade sealant", "GAF TopCoat FlexSeal #8962920WP", GE, "Tube", None, "", 14.00, 0, "Manual", D(2026, 10, 20), "769 NE 74th Rev 2", None, None, "Coverage unknown — manual qty."),
    ("TPO-CUTEDGE", "TPO", "TPO cut-edge sealant (pint)", "GAF", GE, "Pint", None, "", None, 0, "Manual", None, "", None, None, "Reinforced TPO cut edges (9139 NE 10th). PRICE NEEDED."),
    ("TPO-FAST", "TPO", "Membrane fastener #14 (mech. attached)", "Drill-Tec #14 x 1.75\"", GE, "EA", 1, "EA", None, 0, "Manual", None, "", None, None, "Count from NOA row spacing (e.g. 25-0707.01 E(4)). PRICE NEEDED."),
    ("TPO-PLATE", "TPO", "Membrane plate 2-3/4\" barbed", "Drill-Tec 2-3/4\" barbed SXHD plate", GE, "EA", 1, "EA", None, 0, "Manual", None, "", None, None, "1 per fastener. PRICE NEEDED."),
    ("TPO-METAL", "TPO", "TPO-coated metal drip edge", "GAF EverGuard TPO-coated metal", GE, "LF", 1, "LF", None, 0.10, "Drip Edge LF", None, "", None, None, "Plus cleats (9139 NE 10th). PRICE NEEDED."),
    # Mod-bit / BUR
    ("MB-PRIMER", "Mod-bit / BUR", "Asphalt primer 5 gal", "Tropical 410", SHOP, "Pail", 500, "SF", 43.48, 0, "Field + Wall SF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "~100 SF/gal (ASTM D41) — confirm."),
    ("MB-STRATAVENT", "Mod-bit / BUR", "Venting base sheet", "GAF StrataVent", SHOP, "Roll", None, "SF", 59.00, 0.10, "Field SF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "Roll coverage unknown — manual qty."),
    ("BUR-PLY4", "Mod-bit / BUR", "Fiberglass ply sheet Type IV", "GAF GAFGLAS #4 Ply Sheet", "", "Roll", 500, "SF", 53.00, 0.10, "Field SF", D(2026, 11, 20), "Marc (9795 SW 170th)", None, None, "5 SQ/roll assumed — confirm. Multiplier = plies."),
    ("BUR-PLY4-WALL", "Mod-bit / BUR", "Fiberglass ply #4 — wall flashing", "GAF GAFGLAS #4 Ply Sheet", "", "Roll", 500, "SF", 53.00, 0.10, "Wall Flashing SF", D(2026, 11, 20), "Marc (9795 SW 170th)", None, None, "Multiplier = plies."),
    ("MB-RUB20", "Mod-bit / BUR", "Smooth ply 1.5 SQ", "GAF Ruberoid 20 smooth", SHOP, "Roll", 150, "SF", 85.00, 0.10, "Field SF", D(2026, 6, 26), "Shop list 6/26/26", None, None, ""),
    ("MB-RUB20-WALL", "Mod-bit / BUR", "Smooth ply — wall flashing", "GAF Ruberoid 20 smooth", SHOP, "Roll", 150, "SF", 85.00, 0.10, "Wall Flashing SF", D(2026, 6, 26), "Shop list 6/26/26", None, None, ""),
    ("MB-CAP", "Mod-bit / BUR", "Granulated cap sheet 1.25 SQ", "GAF Capsheet (granulated)", SHOP, "Roll", 125, "SF", 59.90, 0.10, "Field SF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "Confirm roll size (1 SQ roll = 100 SF)."),
    ("MB-CAP-WALL", "Mod-bit / BUR", "Granulated cap — wall flashing", "GAF Capsheet (granulated)", SHOP, "Roll", 125, "SF", 59.90, 0.10, "Wall Flashing SF", D(2026, 6, 26), "Shop list 6/26/26", None, None, ""),
    ("MB-ASPHALT", "Mod-bit / BUR", "Hot asphalt Type III, 100-lb keg", "Asphalt (shop 'Asphalt (24)')", SHOP, "Keg", 400, "SF", 40.00, 0.10, "Field SF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "25 lb/SQ per mopped layer = 400 SF/keg. Multiplier = mopped layers. Match NOA rate."),
    ("MB-CANT", "Mod-bit / BUR", "Cant strip (84 LF/unit)", "Cant strip 1x4", SHOP, "EA", 84, "LF", 40.00, 0.10, "Wall Flashing LF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "Confirm unit."),
    ("MB-FLCEM", "Mod-bit / BUR", "Flashing cement", "Tropical 2100", SHOP, "Tube", 12, "LF", 6.15, 0.10, "Wall Flashing LF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "12 LF/tube. Use basis Drip Edge LF under edge metal."),
    ("MB-GRAN", "Mod-bit / BUR", "Granules (touch-up)", "Granule bag", SHOP, "Bag", 1, "JOB", 19.80, 0, "Manual", D(2026, 6, 26), "Shop list 6/26/26", None, None, ""),
    # Insulation / board
    ("ISO-TAPER-LS", "Insulation", "Tapered ISO system (supplier quote)", "Gulfeagle tapered quote", GE, "LS", 1, "JOB", None, 0, "Per Job", None, "", None, None, "Enter the quote $ in Unit Cost Override. Recent: #26-2928 $10,387 (35.2 SQ, 10/19/26); 769 NE 74th $12,929 (23.4 SQ)."),
    ("ISO-ADH", "Insulation", "Insulation adhesive", "OlyBond 500", "", "EA", None, "", 1080.00, 0, "Manual", D(2026, 10, 20), "769 NE 74th Rev 1 (Marc)", None, None, "Coverage per NOA — manual qty."),
    ("BUR-HDBOARD", "Insulation", "1/2\" HD cover board 4'x4'", "HD board (polyiso or gypsum)", "", "Board", 16, "SF", 16.00, 0.10, "Field SF", D(2026, 11, 20), "Marc (9795 SW 170th)", None, None, "$16 per 4'x4' board."),
    # Edge metal / flashing
    ("DRIPEDGE-3X3", "Edge metal", "Drip edge 3\"x3\" 10'", "3\"x3\" drip edge (gauge/metal TBD)", "", "PC", 10, "LF", 8.50, 0.10, "Drip Edge LF", D(2026, 11, 20), "Marc (9795 SW 170th)", None, None, "Also used to build pitch pans on site."),
    ("DRIPEDGE", "Edge metal", "Drip edge (other profile)", "Gauge / metal TBD", "", "PC", 10, "LF", None, 0.10, "Drip Edge LF", None, "", None, None, "A1. PRICE NEEDED."),
    ("LFLASH", "Edge metal", "L-flashing / sidewall 10'", "Gauge / metal TBD", "", "PC", 10, "LF", None, 0.10, "L-Flashing LF", None, "", None, None, "PRICE NEEDED."),
    ("TERMBAR", "Edge metal", "Termination bar flat 10'", "OMG flat alum #FLATB06", GE, "PC", 10, "LF", 8.00, 0.10, "Wall Flashing LF", D(2026, 10, 20), "Price book (769 NE 74th)", 6.85, D(2024, 12, 12), "Multiplier = rows."),
    ("TERMBAR-LIP", "Edge metal", "Termination bar with lip 10'", "OMG lip alum #LIPTB06", GE, "PC", 10, "LF", 7.75, 0.10, "Wall Flashing LF", D(2024, 12, 12), "Gulfeagle quote S002031839", None, None, "Quote expired — reconfirm."),
    ("STUCCOSTOP", "Edge metal", "Counterflashing stucco stop 5\" 26 ga 10'", "Stucco stop galv", "", "PC", 10, "LF", 8.15, 0.10, "Wall Flashing LF", D(2026, 10, 20), "Price book (769 NE 74th)", None, None, "Alt: 2-part SS reglet — price TBD."),
    ("COPING", "Edge metal", "Metal coping cap", "Gauge / finish TBD", "", "LF", 1, "LF", None, 0.10, "Coping LF", None, "", None, None, "Sheet-metal quote. PRICE NEEDED."),
    ("COPING-CLEAT", "Edge metal", "Continuous coping cleat", "Gauge TBD", "", "LF", 1, "LF", None, 0.10, "Coping LF", None, "", None, None, "Multiplier 2 = both faces. PRICE NEEDED."),
    ("VALLEY-MTL", "Edge metal", "Valley metal 10'", "Gauge / metal TBD", "", "PC", 10, "LF", None, 0.10, "Valley LF", None, "", None, None, "PRICE NEEDED."),
    ("PITCHPAN", "Edge metal", "Pitch pan (purchased)", "Galvanized, size to leg", "", "EA", 1, "EA", None, 0, "Equipment Legs EA", None, "", None, None, "Or build on site from 3x3 drip edge. PRICE NEEDED."),
    ("PP-FILLER", "Edge metal", "Pitch pan filler / pourable sealer", "Product TBD", "", "EA", 1, "EA", None, 0, "Equipment Legs EA", None, "", None, None, "1 per pan assumed. PRICE NEEDED."),
    # Fasteners / sealants / lumber
    ("ANCHOR", "Fasteners", "Masonry anchors 1/4\"x1-1/4\" (100/box)", "OMG #MA114X", GE, "Box", 100, "EA", 9.00, 0.10, "Wall Flashing LF", D(2026, 10, 20), "Price book (769 NE 74th)", None, None, "1/LF @ 12\" o.c. Multiplier = rows."),
    ("TAPCON", "Fasteners", "Tapcon 1/4\"x1-3/4\" (100/box)", "Tapcon concrete screw", "", "Box", 100, "EA", None, 0.10, "Drip Edge LF", None, "", None, None, "Nailer to concrete, 12\" o.c. assumed (RAS 111). PRICE NEEDED."),
    ("NAIL-RS114", "Fasteners", "Ring shank nails 1-1/4\" Miami-Dade approved", "Galv. ring shank roofing nail", "", "EA", 1, "EA", None, 0.10, "Drip Edge LF", None, "", None, None, "Edge metal to nailer. Multiplier 3 = 4\" o.c. Box size TBD. PRICE NEEDED."),
    ("SEAL-915", "Sealants", "Sealant (top of counterflashing)", "Bostik 915 white", SHOP, "Tube", 12, "LF", 4.90, 0.10, "Wall Flashing LF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "12 LF/tube."),
    ("NAILER-1X6", "Lumber", "Wood nailer 1x6 PT 10'", "1x6x10 pressure-treated", "", "PC", 10, "LF", 5.95, 0.10, "Drip Edge LF", D(2026, 11, 20), "Marc (9795 SW 170th)", None, None, "Perimeter nailer under edge metal."),
    ("NAILER-2X8", "Lumber", "Wood nailer 2x8 10'", "2x8x10 (confirm PT)", SHOP, "PC", 10, "LF", 10.85, 0.10, "Coping LF", D(2026, 6, 26), "Shop list 6/26/26", None, None, "Parapet top nailer."),
    # Underlayments (handoff presets)
    ("T-TILESEAL", "Underlayment", "TileSeal (T1 / T2 top)", "Westlake TileSeal", "", "Roll", 200, "SF", None, "Job", "Field SF", None, "", None, None, "2.0 SQ net/roll. Open Item 2: roll size. PRICE NEEDED."),
    ("T-CITADEL", "Underlayment", "Citadel PRO base (T2)", "Westlake Citadel PRO FL14317", "", "Roll", 200, "SF", None, "Job", "Field SF", None, "", None, None, "2.0 SQ net/roll. PRICE NEEDED."),
    ("T-FLSACAP", "Underlayment", "Flintlastic SA Cap (T3)", "CertainTeed Flintlastic SA Cap", "", "Roll", 100, "SF", None, "Job", "Field SF", None, "", None, None, "1.0 SQ. Open Item 1 (T3). PRICE NEEDED."),
    ("UM-XFR", "Underlayment", "Polystick XFR (U-M1)", "Polyglass Polystick XFR", "", "Roll", 150, "SF", None, "Job", "Field SF", None, "", None, None, "1.5 SQ net; 265F. PRICE NEEDED."),
    ("L-ELASTOBASE", "Underlayment", "Elastobase base, mech. attached (L1)", "Polyglass Elastobase", "", "Roll", 200, "SF", None, 0.10, "Field SF", None, "", None, None, "2.0 SQ. PRICE NEEDED."),
    ("L-SAV", "Underlayment", "Elastoflex SA V base (L2)", "Polyglass Elastoflex SA V", "", "Roll", 200, "SF", None, 0.10, "Field + Wall SF", None, "", None, None, "2.0 SQ. PRICE NEEDED."),
    ("L-SAP", "Underlayment", "Elastoflex SA P cap (L1/L2)", "Polyglass Elastoflex SA P", "", "Roll", 100, "SF", None, 0.10, "Field + Wall SF", None, "", None, None, "1.0 SQ. Open Item 3. PRICE NEEDED."),
    ("L-NAILBASE", "Underlayment", "Flintlastic SA NailBase (L3)", "CertainTeed Flintlastic SA NailBase", "", "Roll", 200, "SF", None, 0.10, "Field SF", None, "", None, None, "2.0 SQ. PRICE NEEDED."),
    ("L-FLCAP", "Underlayment", "Flintlastic SA Cap (L3 cap)", "CertainTeed Flintlastic SA Cap", "", "Roll", 100, "SF", None, 0.10, "Field + Wall SF", None, "", None, None, "1.0 SQ. PRICE NEEDED."),
    # Tile
    ("TILE-FIELD", "Tile", "Field tile (order by SQ)", "Profile / color TBD", "", "SQ", 100, "SF", None, "Job", "Field SF", None, "", None, None, "Pcs/SQ from manufacturer sheet — never assumed. PRICE NEEDED."),
    ("TILE-HR", "Tile", "Hip & ridge trim (order by LF)", "Profile TBD", "", "LF", 1, "LF", None, "Job", "Hip & Ridge LF", None, "", None, None, "Pcs/LF from manufacturer sheet. PRICE NEEDED."),
    ("TILE-EAVECL", "Tile", "Eave closure", "Per tile profile", "", "LF", 1, "LF", None, "Job", "Eave LF", None, "", None, None, "PRICE NEEDED."),
    ("TILE-ADH", "Tile", "Tile adhesive (foam paddies)", "Per NOA attachment table", "", "Kit", None, "", None, 0.05, "Manual", None, "", None, None, "Qty per NOA table and zone pressures. PRICE NEEDED."),
    # Tools / consumables
    ("TOOL-BRUSH", "Tools", "Brush 4\"", "Brush 4", SHOP, "EA", 1, "EA", 1.47, 0, "Manual", D(2026, 6, 26), "Shop list 6/26/26", None, None, ""),
    ("TOOL-BIT", "Tools", "Masonry drill bit", "Drill bits", SHOP, "EA", 1, "EA", 2.64, 0, "Manual", D(2026, 6, 26), "Shop list 6/26/26", None, None, ""),
    ("TOOL-RFRAME", "Tools", "Roller frame 9\" HD", "C&R #RF9HDN1", GE, "EA", 1, "EA", 2.70, 0, "Manual", D(2026, 2, 5), "Gulfeagle inv 2/5/26", None, None, ""),
    ("TOOL-RCOVER", "Tools", "Roller cover 9\" 3/4\" nap", "C&R #RC9-3/4", GE, "EA", 1, "EA", 1.65, 0, "Manual", D(2026, 2, 5), "Gulfeagle inv 2/5/26", None, None, ""),
    ("TOOL-MOP", "Tools", "Mop", "Mop", SHOP, "EA", 1, "EA", 7.15, 0, "Manual", D(2026, 6, 26), "Shop list 6/26/26", None, None, ""),
]
PB_COLS = ["Code", "Category", "Item", "Product / SKU", "Supplier", "Order Unit", "Coverage / Unit", "Cov. Unit",
           "Unit Cost ($)", "Default Waste", "Default Basis", "Price Date", "Price Source", "Age (days)",
           "Prev. Cost ($)", "Prev. Date", "Notes / Status"]
PB_WIDTHS = [15, 13, 34, 30, 11, 8, 9, 7, 10, 9, 17, 10, 24, 8, 10, 10, 50]

# Systems: key -> (name, [(code, basis override, multiplier, manual qty)])
SYSTEMS = {
    "blank": ("Blank — type your own codes", []),
    "tpo-fa": ("TPO fully adhered over tapered ISO (concrete)", [
        ("ISO-TAPER-LS", None, 1, None), ("ISO-ADH", None, 1, None), ("TPO-060", "Field + Wall SF", 1, None),
        ("TPO-UN55", None, 1, 1), ("TPO-1121", "Field + Wall SF", 1, None), ("TPO-CLEAN", None, 1, None),
        ("TPO-TJOINT", None, 1, None), ("TPO-BOOT-2", None, 1, None), ("TPO-BOOT-5", None, 1, None),
        ("TPO-SCUP", None, 1, None), ("TERMBAR", None, 2, None), ("ANCHOR", None, 3, None), ("STUCCOSTOP", None, 1, None),
        ("TPO-WBLOCK", None, 1, None), ("TPO-FLEX", None, 1, None), ("TOOL-BRUSH", None, 1, 6), ("TOOL-BIT", None, 1, 6),
        ("TOOL-RFRAME", None, 1, 4), ("TOOL-RCOVER", None, 1, 12), ("TOOL-MOP", None, 1, 2)]),
    "tpo-ma": ("TPO mechanically attached (wood deck)", [
        ("TPO-060", "Field + Wall SF", 1, None), ("TPO-UN55", None, 1, 1), ("TPO-FAST", None, 1, None), ("TPO-PLATE", None, 1, None),
        ("TPO-1121-WALL", None, 1, None), ("TPO-CLEAN", None, 1, None), ("TPO-TJOINT", None, 1, None), ("TPO-CUTEDGE", None, 1, None),
        ("TPO-BOOT-2", None, 1, None), ("TPO-BOOT-5", None, 1, None), ("TERMBAR", None, 1, None), ("NAILER-2X8", None, 1, None),
        ("COPING", None, 1, None), ("COPING-CLEAT", None, 2, None), ("TPO-METAL", None, 1, None), ("TOOL-BRUSH", None, 1, 6),
        ("TOOL-RFRAME", None, 1, 4), ("TOOL-RCOVER", None, 1, 12)]),
    "bur-eave": ("Hot-mop BUR, open eave: HD board + 2 ply #4 + cap (concrete)", [
        ("MB-PRIMER", None, 1, None), ("BUR-HDBOARD", None, 1, None), ("BUR-PLY4", None, 2, None), ("MB-CAP", None, 1, None),
        ("MB-ASPHALT", None, 4, None), ("NAILER-1X6", None, 1, None), ("TAPCON", None, 1, None), ("DRIPEDGE-3X3", None, 1, None),
        ("NAIL-RS114", None, 3, None), ("MB-FLCEM", "Drip Edge LF", 1, None), ("DRIPEDGE-3X3", "Manual", 1, 2),
        ("PP-FILLER", "Equipment Legs EA", 1, None), ("MB-GRAN", None, 1, 2), ("TOOL-MOP", None, 1, 6), ("TOOL-BRUSH", None, 1, 6)]),
    "bur-parapet": ("Hot-mop BUR with parapets: HD board + 2 ply #4 + cap (concrete)", [
        ("MB-PRIMER", None, 1, None), ("BUR-HDBOARD", None, 1, None), ("BUR-PLY4", None, 2, None), ("MB-CAP", None, 1, None),
        ("MB-ASPHALT", None, 4, None), ("BUR-PLY4-WALL", None, 2, None), ("MB-CAP-WALL", None, 1, None),
        ("MB-ASPHALT", "Wall Flashing SF", 3, None), ("MB-CANT", None, 1, None), ("TERMBAR", None, 1, None),
        ("STUCCOSTOP", None, 1, None), ("ANCHOR", None, 2, None), ("MB-FLCEM", None, 1, None), ("SEAL-915", None, 1, None),
        ("MB-GRAN", None, 1, 2), ("TOOL-MOP", None, 1, 6), ("TOOL-BRUSH", None, 1, 6)]),
    "modbit-hot": ("Mod-bit hot mop over tapered ISO (StrataVent + Ruberoid 20 + cap)", [
        ("MB-PRIMER", None, 1, None), ("ISO-TAPER-LS", None, 1, None), ("MB-STRATAVENT", None, 1, None), ("MB-RUB20", None, 1, None),
        ("MB-RUB20-WALL", None, 1, None), ("MB-CAP", None, 1, None), ("MB-CAP-WALL", None, 1, None), ("MB-ASPHALT", None, 3, None),
        ("MB-CANT", None, 1, None), ("TERMBAR", None, 1, None), ("STUCCOSTOP", None, 1, None), ("ANCHOR", None, 2, None),
        ("MB-FLCEM", None, 1, None), ("SEAL-915", None, 1, None), ("MB-GRAN", None, 1, 2), ("TOOL-MOP", None, 1, 6),
        ("TOOL-BRUSH", None, 1, 6)]),
    "sa-2ply": ("Low-slope SA 2-ply (L2: Elastoflex SA V + SA P)", [
        ("MB-PRIMER", None, 1, None), ("L-SAV", None, 1, None), ("L-SAP", None, 1, None), ("DRIPEDGE", None, 1, None),
        ("TERMBAR", None, 1, None), ("STUCCOSTOP", None, 1, None), ("ANCHOR", None, 2, None), ("SEAL-915", None, 1, None),
        ("TOOL-BRUSH", None, 1, 6)]),
    "tile-t1": ("Tile (C1) + T1 TileSeal direct to deck", [
        ("TILE-FIELD", None, 1, None), ("TILE-HR", None, 1, None), ("TILE-EAVECL", None, 1, None), ("T-TILESEAL", None, 1, None),
        ("TILE-ADH", None, 1, None), ("DRIPEDGE", None, 1, None), ("LFLASH", None, 1, None), ("VALLEY-MTL", None, 1, None)]),
    "tile-t2": ("Tile (C1/C2) + T2 Citadel PRO + TileSeal", [
        ("TILE-FIELD", None, 1, None), ("TILE-HR", None, 1, None), ("TILE-EAVECL", None, 1, None), ("T-CITADEL", None, 1, None),
        ("T-TILESEAL", None, 1, None), ("TILE-ADH", None, 1, None), ("DRIPEDGE", None, 1, None), ("LFLASH", None, 1, None),
        ("VALLEY-MTL", None, 1, None)]),
}
DEFAULT_SYSTEM = "tpo-fa"

JOB_HISTORY = [
    # date, job, system, field SF, material total incl tax, notes
    (D(2026, 10, 20), "769 NE 74th St (Rev 2)", "TPO fully adhered + tapered ISO", 2439.86, 26285.50, "Incl. tapered ISO $12,929"),
    (D(2026, 10, 20), "9139 NE 10th Ave (Rev 1)", "TPO mech. attached, wood deck", 4628.0, 8819.66, "Priced lines only; fasteners, coping, metal TBD"),
    (D(2026, 10, 20), "9730 E Indigo St (Rev 1)", "Mod-bit hot mop + tapered ISO", 3394.7, 20032.98, "Incl. tapered ISO $10,387"),
    (D(2026, 11, 20), "9795 SW 170th St (Rev 0)", "Hot-mop BUR, open eave", 2021.25, 5813.22, "Tapcons, nails, pitch-pan filler TBD"),
]

LINES = 60
FIRST = 8


def hdr(ws, row, labels, widths=None):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
        c.alignment = Alignment(wrap_text=True, vertical="center")
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def name(wb, nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)


def existing_price_book(path):
    """Read the Price Book rows from an existing master so prices survive a rebuild."""
    if not os.path.exists(path):
        return None
    ws = load_workbook(path)["Price Book"]
    rows = []
    for r in range(4, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, len(PB_COLS) + 1)]
        if vals[0]:
            vals[13] = None  # Age is a formula
            rows.append(vals)
    return rows


def existing_tabs(path):
    """Systems, lines, price log and job history from an existing master (None if no master)."""
    if not os.path.exists(path):
        return None
    wb = load_workbook(path)
    a = wb["Assemblies"]
    systems, lines = {}, {}
    for r in range(4, a.max_row + 1):
        nm, k = a.cell(r, 1).value, a.cell(r, 2).value
        if nm and k:
            systems[k] = nm
    for r in range(4, a.max_row + 1):
        k, n, code, bo, mult, man = [a.cell(r, c).value for c in range(4, 10)]
        if k and code:
            lines.setdefault(k, []).append((n or 0, code, bo, mult, man))
    sysd = {k: (systems[k], [(c, b, m, q) for _, c, b, m, q in sorted(lines.get(k, []), key=lambda x: x[0])])
            for k in systems}
    lg = wb["Price Log"]
    log = [tuple(lg.cell(r, c).value for c in (1, 2, 4, 5, 7, 8, 9)) for r in range(4, lg.max_row + 1)
           if lg.cell(r, 2).value]
    jh = wb["Job History"]
    hist = [tuple(jh.cell(r, c).value for c in (1, 2, 3, 4, 6, 8)) for r in range(4, jh.max_row + 1)
            if jh.cell(r, 2).value]
    return sysd, log, hist


SEED_LOG = [(D(2026, 11, 20), "BUR-HDBOARD", None, 16.00, "", "Marc (9795 SW 170th)", "Marc"),
            (D(2026, 11, 20), "BUR-PLY4", None, 53.00, "", "Marc (9795 SW 170th)", "Marc"),
            (D(2026, 11, 20), "DRIPEDGE-3X3", None, 8.50, "", "Marc (9795 SW 170th)", "Marc"),
            (D(2026, 11, 20), "NAILER-1X6", None, 5.95, "", "Marc (9795 SW 170th)", "Marc"),
            (D(2026, 3, 30), "TPO-UN55", 376.28, 360.00, GE, "Gulfeagle inv 3/30/26 (was quote 12/12/24)", ""),
            (D(2026, 3, 30), "TPO-1121", 165.54, 170.00, GE, "Gulfeagle inv 3/30/26 (was quote 12/12/24)", "")]


def build(out, pb_rows, systems=None, log0=None, history=None):
    systems = systems or SYSTEMS
    log0 = SEED_LOG if log0 is None else log0
    history = JOB_HISTORY if history is None else history
    wb = Workbook()

    # ================= Start Here =================
    st = wb.active
    st.title = "Start Here"
    st.column_dimensions["A"].width = 110
    lines = [
        ("MASTER TAKEOFF & COST BUILDER — M. Romero's Roofing & Inspections, Inc.", Font(bold=True, size=14)),
        ("Use this file for every job. Keep the master clean: File > Save As a job copy first.", Font(italic=True)),
        ("", None),
        ("NEW JOB", BOLD),
        ("1. Save As  takeoffs/xlsx/YYYY-MM-DD_<job>_Takeoff_Rev0.xlsx", None),
        ("2. Inputs tab: pick the SYSTEM from the dropdown, fill job info, permitting data, measurements, waste %, tax.", None),
        ("3. Takeoff tab: the system's lines load automatically. Adjust any line:", None),
        ("     • Include = N drops a line.   • Type a new Code in a blank row to add an item (dropdown).", None),
        ("     • Blue columns are adjustments: Basis, Multiplier (rows / plies / layers), Waste, Manual Order Qty, Unit Cost Override.", None),
        ("     • Typing over a loaded value (Code, Basis, Multiplier, Manual Qty) replaces it for this job only.", None),
        ("4. Enter dump truck, permit, permit runner, etc. under OTHER JOB COSTS (no sales tax).", None),
        ("5. Check the Flag column: PRICE NEEDED / ENTER MEASUREMENT / ENTER MANUAL QTY / UNKNOWN CODE. Totals cover priced lines only.", None),
        ("", None),
        ("NEW PRICES (do this in the MASTER, so every future job gets them)", BOLD),
        ("1. Price Book tab: copy the old Unit Cost + Price Date into Prev. Cost / Prev. Date, then type the new cost, date and source.", None),
        ("2. Add a row in Price Log (date, code, old, new, source).", None),
        ("3. New item: add a row at the bottom of the Price Book with a unique Code. It shows up in the Code dropdown right away.", None),
        ("   Yellow = no price yet.  Orange = price older than %d days — reconfirm before ordering." % STALE_DAYS, None),
        ("", None),
        ("NEW SYSTEM", BOLD),
        ("Assemblies tab: add the system name to the Systems list and its lines (Line 1, 2, 3...) to the Lines table. It appears in the Inputs dropdown.", None),
        ("", None),
        ("RULES (handoff prompt)", BOLD),
        ("• Never guess dimensions, pitch, pressures, deck type or NOA numbers — leave them blank; the Inputs tab counts what is missing.", None),
        ("• Waste: 10% gable · 15% hip · 18-22% cut-up; +5-10% cut buffer for tile/metal. Net roll coverage already includes laps.", None),
        ("• Roof area from drip-edge polygons or Bluebeam, never floor area. Confirm every NOA / FL# before ordering.", None),
    ]
    for i, (t, f) in enumerate(lines, 1):
        c = st.cell(row=i, column=1, value=t)
        if f:
            c.font = f

    # ================= Inputs =================
    ws = wb.create_sheet("Inputs")
    for col, w in zip("ABCD", (34, 46, 10, 70)):
        ws.column_dimensions[col].width = w
    ws["A1"] = "JOB INPUTS"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = "Blue = input. Yellow = still blank."
    ws["A2"].font = Font(italic=True)
    ws["A4"] = "SYSTEM"
    ws["A4"].font = Font(bold=True, size=12)
    ws["B4"] = systems[DEFAULT_SYSTEM][0] if DEFAULT_SYSTEM in systems else next(iter(systems.values()))[0]
    ws["B4"].font = Font(bold=True, color="0000CC", size=12)
    ws["B4"].fill = YELLOW
    ws["D4"] = "Pick from the dropdown. Lines load on the Takeoff tab."
    name(wb, "SysName", "Inputs!$B$4")
    r = 6
    ws.cell(r, 1, "JOB").font = BOLD
    ws.cell(r, 1).fill = SEC_FILL
    job_rows = {}
    for lab, val in [("Job name / address", None), ("Date", None), ("Revision", "Rev 0"), ("Option / scope", None),
                     ("Plan set / report / sketch", None), ("Prepared by", None)]:
        r += 1
        ws.cell(r, 1, lab)
        c = ws.cell(r, 2, val)
        c.font = BLUE
        job_rows[lab] = r
    r += 2
    ws.cell(r, 1, "CRITICAL MISSING DATA FOR MIAMI-DADE PERMITTING").font = BOLD
    ws.cell(r, 1).fill = SEC_FILL
    c0 = r + 1
    for lab in ["Wind zone (HVHZ?)", "Roof slope / pitch", "Mean roof height (ft)", "Risk Category", "Exposure Category",
                "Zone 1 pressure (psf)", "Zone 2 pressure (psf)", "Zone 3 pressure (psf)", "Deck type & condition",
                "New / re-roof (layers to remove)", "Covering / membrane NOA / FL#", "Base / underlayment NOA / FL#",
                "Insulation / board NOA / FL#", "Edge metal NOA / FL#"]:
        r += 1
        ws.cell(r, 1, lab)
        ws.cell(r, 2).font = BLUE
    c1 = r
    ws.conditional_formatting.add(f"B{c0}:B{c1}", FormulaRule(formula=[f"LEN(B{c0})=0"], fill=YELLOW))
    r += 1
    ws.cell(r, 1, "Missing permitting items")
    ws.cell(r, 2, f"=COUNTBLANK(B{c0}:B{c1})").font = RED_FONT
    name(wb, "MissingCount", f"Inputs!$B${r}")
    r += 2
    ws.cell(r, 1, "WASTE & TAX").font = BOLD
    ws.cell(r, 1).fill = SEC_FILL
    r += 1
    ws.cell(r, 1, "Field waste % (items set to 'Job')")
    c = ws.cell(r, 2, 0.10)
    c.font, c.number_format = BLUE, PCT
    ws.cell(r, 4, "10% gable / flat · 15% hip · 18-22% cut-up. +5-10% for tile/metal.")
    name(wb, "JobWaste", f"Inputs!$B${r}")
    r += 1
    ws.cell(r, 1, "Sales tax rate (materials)")
    c = ws.cell(r, 2, 0.07)
    c.font, c.number_format = BLUE, PCT
    name(wb, "TaxRate", f"Inputs!$B${r}")
    r += 2
    ws.cell(r, 1, "MEASUREMENTS").font = BOLD
    ws.cell(r, 1).fill = SEC_FILL
    r += 1
    for i, lab in enumerate(["Basis", "Value", "Unit", "Source / Note"], 1):
        c = ws.cell(r, i, lab)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
    b0 = r + 1
    brow = {n: b0 + i for i, (n, *_) in enumerate(BASIS)}
    for n, kind, unit, note in BASIS:
        rr = brow[n]
        ws.cell(rr, 1, n).border = BOX
        if kind == "in":
            c = ws.cell(rr, 2)
            c.font = BLUE
        else:
            f = kind
            for k, v in brow.items():
                f = f.replace("{" + k + "}", f"B{v}")
            c = ws.cell(rr, 2, f)
        c.number_format, c.border = NUM, BOX
        ws.cell(rr, 3, unit).border = BOX
        c = ws.cell(rr, 4, note)
        c.border = BOX
        c.font = BLUE
    b1 = b0 + len(BASIS) - 1
    name(wb, "BasisNames", f"Inputs!$A${b0}:$A${b1}")
    name(wb, "BasisValues", f"Inputs!$B${b0}:$B${b1}")
    r = b1 + 1
    ws.cell(r, 1, "Field SQ (calculated)")
    ws.cell(r, 2, f"=B{brow['Field SF']}/100").number_format = NUM
    ws.cell(r, 3, "SQ")
    name(wb, "FieldSQ", f"Inputs!$B${r}")
    fs = brow["Field SF"]
    ws.conditional_formatting.add(f"B{fs}", FormulaRule(formula=[f"LEN(B{fs})=0"], fill=YELLOW))
    ws.freeze_panes = "A5"

    # ================= Price Book =================
    pb = wb.create_sheet("Price Book")
    pb["A1"] = "PRICE BOOK — the master price list. Update prices here (see Start Here). Yellow = no price. Orange = older than %d days." % STALE_DAYS
    pb["A1"].font = BOLD
    hdr(pb, 3, PB_COLS, PB_WIDTHS)
    pb.row_dimensions[3].height = 30
    end = 3 + len(pb_rows) + 150
    for i, row in enumerate(pb_rows):
        rr = 4 + i
        for j, v in enumerate(row, 1):
            pb.cell(rr, j, v)
    for rr in range(4, end + 1):
        pb.cell(rr, 14, f'=IF(L{rr}="","",TODAY()-L{rr})')
        for j in range(1, len(PB_COLS) + 1):
            c = pb.cell(rr, j)
            c.border = BOX
            c.alignment = WRAP
            if j in (7, 9, 10, 12, 13, 15, 16):
                c.font = BLUE
        pb.cell(rr, 9).number_format = MONEY
        pb.cell(rr, 15).number_format = MONEY
        pb.cell(rr, 10).number_format = PCT
        pb.cell(rr, 12).number_format = DATE
        pb.cell(rr, 16).number_format = DATE
    pb.conditional_formatting.add(f"I4:I{end}", FormulaRule(formula=['AND($A4<>"",LEN($I4)=0)'], fill=YELLOW))
    pb.conditional_formatting.add(f"L4:N{end}", FormulaRule(formula=[f'AND($I4<>"",ISNUMBER($N4),$N4>{STALE_DAYS})'], fill=ORANGE))
    for col, nm in [("A", "PB_Code"), ("C", "PB_Item"), ("D", "PB_Product"), ("F", "PB_Unit"), ("G", "PB_Cov"),
                    ("I", "PB_Cost"), ("J", "PB_Waste"), ("K", "PB_Basis"), ("L", "PB_Date")]:
        name(wb, nm, f"'Price Book'!${col}$4:${col}${end}")
    dv = DataValidation(type="list", formula1="=BasisNames", allow_blank=True)
    pb.add_data_validation(dv)
    dv.add(f"K4:K{end}")
    pb.freeze_panes = "C4"
    pb.auto_filter.ref = f"A3:Q{end}"

    # ================= Assemblies =================
    asm = wb.create_sheet("Assemblies")
    asm["A1"] = "SYSTEMS & LINE SETS — edit freely. Each system's lines load on the Takeoff tab when it is picked on Inputs."
    asm["A1"].font = BOLD
    hdr(asm, 3, ["System name (dropdown)", "Key"], None)
    asm.column_dimensions["A"].width = 62
    asm.column_dimensions["B"].width = 12
    s_end = 3 + len(systems) + 20
    for i, (k, (nm, _)) in enumerate(systems.items()):
        asm.cell(4 + i, 1, nm)
        asm.cell(4 + i, 2, k)
    for rr in range(4, s_end + 1):
        for cc in (1, 2):
            asm.cell(rr, cc).border = BOX
            asm.cell(rr, cc).font = BLUE
    name(wb, "Sys_Names", f"Assemblies!$A$4:$A${s_end}")
    name(wb, "Sys_Keys", f"Assemblies!$B$4:$B${s_end}")
    # lines table to the right
    lc = 4  # column D
    heads = ["Key", "Line", "Code", "Basis Override", "Multiplier", "Manual Qty", "KeyLine"]
    for i, h in enumerate(heads):
        c = asm.cell(3, lc + i, h)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
    for i, w in enumerate([12, 6, 16, 18, 10, 10, 16]):
        asm.column_dimensions[get_column_letter(lc + i)].width = w
    rr = 4
    for k, (_, ls) in systems.items():
        for n, (code, bo, mult, man) in enumerate(ls, 1):
            for i, v in enumerate([k, n, code, bo, mult, man]):
                asm.cell(rr, lc + i, v)
            rr += 1
    l_end = rr - 1 + 300
    K, L_, C_, B_, M_, Q_, KL = [get_column_letter(lc + i) for i in range(7)]
    for r2 in range(4, l_end + 1):
        asm[f"{KL}{r2}"] = f'=IF({K}{r2}="","",{K}{r2}&"|"&{L_}{r2})'
        for i in range(7):
            c = asm.cell(r2, lc + i)
            c.border = BOX
            if i < 6:
                c.font = BLUE
        asm[f"{KL}{r2}"].fill = GREY
    for col, nm in [(C_, "Asm_Code"), (B_, "Asm_Basis"), (M_, "Asm_Mult"), (Q_, "Asm_Manual"), (KL, "Asm_KL")]:
        name(wb, nm, f"Assemblies!${col}$4:${col}${l_end}")
    dvc = DataValidation(type="list", formula1="=PB_Code", allow_blank=True)
    dvb = DataValidation(type="list", formula1="=BasisNames", allow_blank=True)
    asm.add_data_validation(dvc)
    asm.add_data_validation(dvb)
    dvc.add(f"{C_}4:{C_}{l_end}")
    dvb.add(f"{B_}4:{B_}{l_end}")
    asm.freeze_panes = "A4"

    # System dropdown on Inputs
    dvs = DataValidation(type="list", formula1="=Sys_Names", allow_blank=False)
    ws.add_data_validation(dvs)
    dvs.add("B4")

    # ================= Takeoff =================
    tk = wb.create_sheet("Takeoff", 1)
    cols = ["Line", "Code", "Include (Y/N)", "Item", "Product / SKU", "Basis", "Basis Used", "Multiplier",
            "Net Qty", "Waste Override", "Waste Used", "Gross Qty", "Coverage / Unit", "Calc Order Qty",
            "Manual Order Qty", "Order Qty", "Unit", "Unit Cost Override", "Unit Cost", "Ext. Cost", "Flag", "Notes / Source"]
    widths = [5, 15, 8, 32, 26, 16, 16, 9, 10, 9, 8, 10, 9, 9, 9, 9, 7, 10, 10, 12, 18, 34]
    tk["A1"] = '="MATERIAL TAKEOFF — "&IF(LEN(Inputs!B7)=0,"(job name)",Inputs!B7)&"  ·  "&Inputs!B9&IF(LEN(Inputs!B10)>0,"  ·  "&Inputs!B10,"")'
    tk["A1"].font = Font(bold=True, size=13)
    tk["A2"] = '="System: "&SysName'
    tk["A2"].font = BOLD
    tk["A3"] = '=IF(MissingCount>0,"⚠ "&MissingCount&" permitting item(s) blank on Inputs. Confirm NOAs before ordering.","Permitting data entered — confirm every NOA / FL# before ordering.")'
    tk["A3"].font = RED_FONT
    tk["A4"] = "Blue columns are adjustments. Order Qty = ROUNDUP(Net x Multiplier x (1+Waste) / Coverage) unless a Manual Order Qty is entered."
    tk["A4"].font = Font(italic=True)
    tk["A5"] = '=IF(ISNA(MATCH(SysName,Sys_Names,0)),"⚠ System not found — pick one on Inputs B4.","")'
    tk["A5"].font = RED_FONT
    hdr(tk, 7, cols, widths)
    tk.row_dimensions[7].height = 32
    tk.column_dimensions["W"].hidden = True
    tk.column_dimensions["X"].hidden = True
    last = FIRST + LINES - 1
    key = 'IFERROR(INDEX(Sys_Keys,MATCH(SysName,Sys_Names,0)),"")'
    for i, rr in enumerate(range(FIRST, last + 1), 1):
        m = f"MATCH($X{rr},Asm_KL,0)"
        pm = f"MATCH($W{rr},PB_Code,0)"

        def pv(nm):  # price-book value; blank cell stays blank in Excel
            return f'IFERROR(IF(INDEX({nm},{pm})&""="","",INDEX({nm},{pm})),"")'

        f = {
            "A": i,
            "X": f'={key}&"|"&$A{rr}',
            "B": f'=IFERROR(T(INDEX(Asm_Code,{m})),"")',
            "C": "Y",
            "W": f'=IF(OR($B{rr}="",UPPER($C{rr})="N"),"",$B{rr})',
            "D": f'=IF($B{rr}="","",IFERROR(T(INDEX(PB_Item,MATCH($B{rr},PB_Code,0))),""))',
            "E": f'=IF($B{rr}="","",IFERROR(T(INDEX(PB_Product,MATCH($B{rr},PB_Code,0))),""))',
            "F": f'=IFERROR(T(INDEX(Asm_Basis,{m})),"")',
            "G": f'=IF($W{rr}="","",IF($F{rr}<>"",$F{rr},{pv("PB_Basis")}))',
            "H": f'=IFERROR(IF(INDEX(Asm_Mult,{m})&""="",1,INDEX(Asm_Mult,{m})),1)',
            "I": f'=IF(OR($W{rr}="",$G{rr}=""),"",IFERROR(INDEX(BasisValues,MATCH($G{rr},BasisNames,0)),0)*N($H{rr}))',
            "K": f'=IF($W{rr}="","",IF($J{rr}<>"",$J{rr},IF({pv("PB_Waste")}="Job",JobWaste,N({pv("PB_Waste")}))))',
            "L": f'=IF($I{rr}="","",$I{rr}*(1+$K{rr}))',
            "M": f'=IF($W{rr}="","",{pv("PB_Cov")})',
            "N": f'=IF(OR($L{rr}="",$M{rr}="",N($M{rr})=0),0,ROUNDUP($L{rr}/$M{rr},0))',
            "O": f'=IFERROR(IF(INDEX(Asm_Manual,{m})&""="","",INDEX(Asm_Manual,{m})),"")',
            "P": f'=IF($W{rr}="","",IF($O{rr}<>"",$O{rr},$N{rr}))',
            "Q": f'=IF($B{rr}="","",IFERROR(T(INDEX(PB_Unit,MATCH($B{rr},PB_Code,0))),""))',
            "S": f'=IF($W{rr}="","",IF($R{rr}<>"",$R{rr},{pv("PB_Cost")}))',
            "T": f'=IF(OR($W{rr}="",$S{rr}=""),0,N($P{rr})*$S{rr})',
            "U": (f'=IF($B{rr}="","",IF(UPPER($C{rr})="N","EXCLUDED",IF(ISNA(MATCH($B{rr},PB_Code,0)),"UNKNOWN CODE",'
                  f'IF($S{rr}="","PRICE NEEDED",IF(AND(N($P{rr})=0,$O{rr}=""),'
                  f'IF(OR($G{rr}="Manual",$M{rr}="",N($M{rr})=0),"ENTER MANUAL QTY","ENTER MEASUREMENT"),"")))))'),
        }
        for col, v in f.items():
            tk[f"{col}{rr}"] = v
        for ci in range(1, 23):
            c = tk.cell(rr, ci)
            c.border = BOX
            if get_column_letter(ci) in ("B", "C", "F", "H", "J", "O", "R", "V"):
                c.font = BLUE
        for col in "ILN":
            tk[f"{col}{rr}"].number_format = "#,##0.##"
        for col in "JK":
            tk[f"{col}{rr}"].number_format = PCT
        for col in "RST":
            tk[f"{col}{rr}"].number_format = MONEY
        tk[f"U{rr}"].font = RED_FONT
        tk[f"A{rr}"].fill = GREY
    dv1 = DataValidation(type="list", formula1="=PB_Code", allow_blank=True)
    dv2 = DataValidation(type="list", formula1="=BasisNames", allow_blank=True)
    dv3 = DataValidation(type="list", formula1='"Y,N"', allow_blank=True)
    for d in (dv1, dv2, dv3):
        tk.add_data_validation(d)
    dv1.add(f"B{FIRST}:B{last}")
    dv2.add(f"F{FIRST}:F{last}")
    dv3.add(f"C{FIRST}:C{last}")
    tk.conditional_formatting.add(f"A{FIRST}:V{last}", FormulaRule(formula=[f'$U{FIRST}="EXCLUDED"'], fill=GREY, font=Font(color="808080")))
    tk.conditional_formatting.add(f"A{FIRST}:V{last}", FormulaRule(formula=[f'LEN($U{FIRST})>0'], fill=YELLOW))

    t = last + 2
    rows_t = [("Material subtotal", f"=SUM(T{FIRST}:T{last})", MONEY),
              ('="Sales tax "&TEXT(TaxRate,"0.0%")', f"=ROUND(T{t}*TaxRate,2)", MONEY),
              ("TOTAL MATERIAL", f"=T{t}+T{t+1}", MONEY),
              ("Material $ per SQ", f'=IF(N(FieldSQ)=0,"",T{t+2}/FieldSQ)', MONEY),
              ("Lines needing price", f'=COUNTIF(U{FIRST}:U{last},"PRICE NEEDED")', "0"),
              ("Other flagged lines", f'=COUNTIF(U{FIRST}:U{last},"?*")-T{t+4}-COUNTIF(U{FIRST}:U{last},"EXCLUDED")', "0")]
    for k, (lab, fml, fmt) in enumerate(rows_t):
        tk[f"S{t+k}"] = lab
        tk[f"T{t+k}"] = fml
        tk[f"S{t+k}"].font = BOLD
        tk[f"T{t+k}"].font = BOLD
        tk[f"T{t+k}"].number_format = fmt
    tk[f"T{t+2}"].fill = SEC_FILL
    tk[f"B{t}"] = "TOTAL covers priced lines only. 'PRICE NEEDED' lines are not in the total. Labor not included."
    tk[f"B{t}"].font = RED_FONT

    h = t + 8
    tk[f"B{h}"] = "OTHER JOB COSTS (no sales tax)"
    tk[f"B{h}"].font = BOLD
    tk[f"B{h}"].fill = SEC_FILL
    tk[f"T{h}"] = "Amount ($)"
    tk[f"T{h}"].font = BOLD
    defaults = ["Dumpster / dump truck (A8)", "Permit fee + NOA package (A9)", "Permit runner", "Crane / hoist", "Engineering / wind calc", "Other"]
    for i, d in enumerate(defaults):
        rr = h + 1 + i
        tk[f"D{rr}"] = d
        for col in ("D", "T"):
            tk[f"{col}{rr}"].font = BLUE
            tk[f"{col}{rr}"].border = BOX
        tk[f"T{rr}"].number_format = MONEY
    e = h + len(defaults)
    tk[f"S{e+1}"] = "Other job costs"
    tk[f"T{e+1}"] = f"=SUM(T{h+1}:T{e})"
    tk[f"S{e+2}"] = "GRAND TOTAL (material + tax + job costs)"
    tk[f"T{e+2}"] = f"=T{t+2}+T{e+1}"
    for k in (1, 2):
        tk[f"S{e+k}"].font = BOLD
        tk[f"T{e+k}"].font = BOLD
        tk[f"T{e+k}"].number_format = MONEY
    tk[f"T{e+2}"].fill = SEC_FILL
    tk.freeze_panes = f"D{FIRST}"
    tk.print_options.gridLines = False
    tk.page_setup.orientation = "landscape"
    tk.page_setup.fitToWidth = 1
    tk.page_setup.fitToHeight = 0
    tk.sheet_properties.pageSetUpPr.fitToPage = True
    tk.print_area = f"A1:V{e+2}"

    # ================= Price Log =================
    lg = wb.create_sheet("Price Log")
    lg["A1"] = "PRICE LOG — one row per price change."
    lg["A1"].font = BOLD
    hdr(lg, 3, ["Date", "Code", "Item", "Old Cost ($)", "New Cost ($)", "Change %", "Supplier", "Source (invoice / quote #)", "Entered by"],
        [10, 15, 34, 11, 11, 9, 12, 30, 12])
    for i in range(200):
        rr = 4 + i
        if i < len(log0):
            for col, v in zip("ABDEGHI", log0[i]):
                lg[f"{col}{rr}"] = v
        lg[f"C{rr}"] = f'=IF(B{rr}="","",IFERROR(INDEX(PB_Item,MATCH(B{rr},PB_Code,0)),""))'
        lg[f"F{rr}"] = f'=IF(OR(D{rr}="",E{rr}=""),"",E{rr}/D{rr}-1)'
        lg[f"A{rr}"].number_format = DATE
        for col in "DE":
            lg[f"{col}{rr}"].number_format = MONEY
        lg[f"F{rr}"].number_format = "0.0%"
        for ci in range(1, 10):
            lg.cell(rr, ci).border = BOX
            if ci not in (3, 6):
                lg.cell(rr, ci).font = BLUE
    dvl = DataValidation(type="list", formula1="=PB_Code", allow_blank=True)
    lg.add_data_validation(dvl)
    dvl.add("B4:B203")
    lg.freeze_panes = "A4"

    # ================= Job History =================
    jh = wb.create_sheet("Job History")
    jh["A1"] = "JOB HISTORY — material totals for a $/SQ sanity check. Add each finished takeoff."
    jh["A1"].font = BOLD
    hdr(jh, 3, ["Date", "Job", "System", "Field SF", "SQ", "Material total (incl. tax)", "$ / SQ", "Notes"],
        [10, 28, 34, 10, 8, 14, 10, 46])
    for i in range(60):
        rr = 4 + i
        if i < len(history):
            for j, v in enumerate(history[i]):
                jh.cell(rr, [1, 2, 3, 4, 6, 8][j], v)
        jh[f"E{rr}"] = f'=IF(D{rr}="","",D{rr}/100)'
        jh[f"G{rr}"] = f'=IF(OR(D{rr}="",F{rr}=""),"",F{rr}/E{rr})'
        jh[f"A{rr}"].number_format = DATE
        jh[f"D{rr}"].number_format = "#,##0.00"
        jh[f"E{rr}"].number_format = "#,##0.00"
        for col in "FG":
            jh[f"{col}{rr}"].number_format = MONEY
        for ci in range(1, 9):
            jh.cell(rr, ci).border = BOX
            if ci not in (5, 7):
                jh.cell(rr, ci).font = BLUE

    for sh in (st, pb, lg, jh, asm):
        sh.page_setup.orientation = "landscape"
        sh.page_setup.fitToWidth = 1
        sh.page_setup.fitToHeight = 0
        sh.sheet_properties.pageSetUpPr.fitToPage = True
    wb.calculation.fullCalcOnLoad = True
    wb.active = 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wb.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fresh", action="store_true", help="reset the Price Book to the seed list in this script")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    rows = None if a.fresh else existing_price_book(a.out)
    tabs = None if a.fresh else existing_tabs(a.out)
    if rows is None:
        rows = [list(r[:13]) + [None] + list(r[13:]) for r in PB]
    sysd, log0, hist = tabs if tabs else (None, None, None)
    print(build(a.out, rows, sysd, log0, hist), f"({len(rows)} price book items, kept existing tabs: {bool(tabs)})")
