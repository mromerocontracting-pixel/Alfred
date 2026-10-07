# Reference Corpus — Proposals, Takeoffs, Plan Sets

Source material for building the blueprint-reading agent. Gathered from Google Drive (`marc.mromerosroofing@gmail.com`) and Gmail on 2026-10-07.

The text in `proposals/` and `takeoffs/` was pulled out of the Drive originals. The originals stay the source of truth. Pricing in these files is historical and is **not** a price book.

## Proposals (most recent first)

| Date | Job | System | Total | Local copy | Drive original |
|---|---|---|---|---|---|
| 2026-10-05 | 4197 Douglas Rd, Miami 33133 | Atlas ISO nail base (3.0" polyiso + 5/8" CDX, R-18.2), copper drip edge, CertainTeed underlayment | $33,892.00 | [proposals/2026-10-05_4197_Douglas_Rd_Nail_Base.md](proposals/2026-10-05_4197_Douglas_Rd_Nail_Base.md) | [PDF](https://drive.google.com/file/d/1pZXRoacQF0O0hf_VYJfwEHXf8qAY096Z/view) |
| 2026-09-15 | The SoBe Room, 1718 Bay Rd, Miami Beach 33139 | TPO roof-to-wall expansion joint, 66 LF @ $65/LF | $4,290.00 | [proposals/2026-09-15_SoBe_Room_Expansion_Joint.md](proposals/2026-09-15_SoBe_Room_Expansion_Joint.md) | [Doc (latest of 4 drafts)](https://docs.google.com/document/d/1JavDeVwqKoG-aosXagQOqU7KpYyMvCQyfKkvLhL5Y3Y/edit) |
| 2026-08-10 | Template (no job) | Soffit/fascia removal, soffit/fascia redesign, flat roof with 1/4" taper | Blank | [proposals/Scopes_of_Work_Template.md](proposals/Scopes_of_Work_Template.md) | [Doc](https://docs.google.com/document/d/1e6U91wzIvvmsOw7gffNzy4bz80sbdHXHMEwlrzgQlUw/edit) |
| 2026-05-19 | 3701 Durango St (repair) | Roof repair | Not read | — | Gmail attachment, sent to the client 2026-05-19 |

## Takeoffs and quote requests

| Date | Job | What it is | Local copy | Drive original |
|---|---|---|---|---|
| 2026-09-02 | Solano Prado, Coral Gables | GAF EverGuard TPO 60-mil fully adhered over tapered ISO on a concrete deck. Three tabs: Assumptions, TPO Takeoff, Price Book. | [takeoffs/2026-09-02_Solano_Prado_TPO_Takeoff_Structure.md](takeoffs/2026-09-02_Solano_Prado_TPO_Takeoff_Structure.md) | [Sheet (latest)](https://docs.google.com/spreadsheets/d/1LMXiBD3DgcTZMM04_TcJQaWMrwQc4lz3z5nONkIO4j8/edit) |
| 2026-08-13 | 6465 SW 23rd St | Tile quote request: Westlake Madera 900, Mountainwood 5001, 36 SQ, 295 LF ridge | [takeoffs/2026-08-13_6465_SW_23rd_Tile_Quote_Request.md](takeoffs/2026-08-13_6465_SW_23rd_Tile_Quote_Request.md) | [Doc](https://docs.google.com/document/d/1gavh_iloR2q7xw8CuxI3lGhw6Vu6Yt4VEso1jMXRVkA/edit) |

## Plan sets (test inputs for the blueprint reader)

These are the blueprints in Drive. They give the agent real sheets to practice on, and the jobs that have a finished proposal or takeoff can be used to check its answers.

| Job | File(s) | Size | Drive |
|---|---|---|---|
| 4197 Douglas Rd | Roof plan and edge detail are embedded in the proposal PDF (Sheets 1–2) | 1.6 MB | [PDF](https://drive.google.com/file/d/1pZXRoacQF0O0hf_VYJfwEHXf8qAY096Z/view) |
| West Regatta (Modrn GC, shared by alberto@modrngc.com) | `2026.0805 - West Regatta - Arch Bid Set.pdf` | 54 MB | [PDF](https://drive.google.com/file/d/1PeI2wOVDgZ_WiGxSihecN3hRfKB110NQ/view) |
| 7741 Ponce de Leon | `7741_Arch.pdf`, A-000 to A-004, A-100, A-101, L-002, S-0, Site Plan, NOA Carrier | 14 MB (arch) | [7741_Arch.pdf](https://drive.google.com/file/d/11JBs_1XljtcpldRozFeNjKNWrSvilnYu/view) |
| 7740 SW 53rd Ave | `PlanSet-7740.sw53rd,ave`, `Permit Set Rev.pdf` (same size, likely the same file) | 4 MB | [PlanSet](https://drive.google.com/file/d/1SiCOfff8aZfzLDFDc8EDsG3UIh_OeR3W/view) |
| 7700 (address unconfirmed) | `7700.ArchPlan-Set.pdf` | 11 MB | [PDF](https://drive.google.com/file/d/1djGM1atPrredVKVtigdsEnVBKPBdTanT/view) |
| Unknown job | `PlanSet48Xx_Arch.pdf` | 20 MB | [PDF](https://drive.google.com/file/d/1wuH-n5tpNlGEGjsuWxhT-JaJ3Ewk6QME/view) |
| 2540 Sauna (Modrn GC) | `2540 Sauna Combined Permit Set.pdf` | 23 MB | [PDF](https://drive.google.com/file/d/1XPWVTlB117WShoDpmKlSzTBo3VcEMu3N/view) |
| 924 NE 14th Pl, Fort Lauderdale | Report or plan PDF (shared by johngoolcharan@gmail.com) | 28 MB | [PDF](https://drive.google.com/file/d/1XBpls0FoBdUV0bAgyPKt906tTwbdhV3f/view) |

## Detail and spec references

| File | Use | Drive |
|---|---|---|
| `GAF-Hot-Asphalt-BUR-HVHZ-Detail-Set.pdf` | HVHZ BUR details; relevant to open item L4 (mod-bit / hot mop) | [PDF](https://drive.google.com/file/d/1KHpgPcURZX0vsCflupiJU95Y8yYF66Wh/view) |
| `Tile-Roof-Details-Homeowner-Guide-p1-12.pdf` | Tile detail guide (two uploads; the 10-05 05:24 copy is the newer one) | [PDF](https://drive.google.com/file/d/19Xpy10S7BO8ENGxTJMpdo-yGZvgzzqna/view) |
| `FL-418889-R2-LMI-MG-350FXW.pdf` | Product approval found in the 7741 Ponce folder | [PDF](https://drive.google.com/file/d/1ObAf_OgsF0x1WYcI9l4rzgzBSdKU74Y4/view) |

## Not found
- `Estimator Setup/HVHZ_Takeoff_Preset_Library.md`. It is not in Drive or in this repo.
- No EagleView or Hover reports turned up in Drive or Gmail.
- No finished takeoff exists yet for a tile or metal job. Solano Prado (TPO) is the only full takeoff workbook.
