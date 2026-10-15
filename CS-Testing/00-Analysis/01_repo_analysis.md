# Repository analysis

Snapshot of `main` at the first push: 13,367 files, about 2.8 GB. All content is under `Components Datasheets/`.

## What is in the repo

| Folder | Size | What it is | Cybersecurity relevance |
|---|---|---|---|
| `Gitlab Files/` | 2.5 GB | Copy of the HIL test-automation project `11_p_01467_mekra_vision_controller` (iTestStudio, Python test pool, vendored libraries, bench-equipment manuals, past test reports) | **High.** It is the place to build cybersecurity test scripts. SOME/IP, DHCP and service-discovery libraries already exist |
| `Functional Safety-Development/` | 130 MB | FuSa work: FSRs, TSRs, technical safety concept, DFMEA, DFA/FTA, SOW1 requirements on SOW2, OPL management sheets, Volvo/Samsung camera interface specs | **High.** The SOW1 interface spec defines the camera authentication scheme (see `02_security_attack_surface.md`). Safe-state and DFMEA data feed fault-handling tests |
| `SoC (CV22FS)/` | 89 MB | Ambarella CV22FS datasheets, Hardware Programming Reference Manual (v1.2 and v1.5), system hardware guide | **High.** Boot configuration (secure boot strap), OTP, JTAG/UART pins |
| `SOW1/` | 23 MB | Samsung S5K3B6SA/SX image-sensor datasheets, app note, imager settings, Volvo camera interface draft | **High.** Sensor-side security (AES-CMAC, key fusing, signed EEPROM) |
| `PHYs/` | 19 MB | NXP TJA1104, TJA1121 (with MACsec core user manual), Microchip LAN887x | **Medium.** MACsec capability. The board uses TJA1104A (100 Mbit) and TJA1121A (1 Gbit) |
| `Test environment description/`, `Analysis/` | 9 MB | Bench description and seven analyses (equipment capability, interface/HW coverage matrix, TSR read/write, register map index) | **High.** Shows what the bench can already do |
| `Schematics/` | 7 MB | MVCU01K BOM02K schematic prints | **High.** JTAG and UART nets, SPI NOR, test points |
| `System Architecture/`, `TSRs/`, `SSRs/` | 11 MB | Polarion exports: architecture, technical safety concept, **software requirements (SRS, includes chapter 23 Cybersecurity)** | **Very high.** Main requirement source |
| `Serializer/`, `Deserializer/`, `PMIC/`, `Flash/`, `DRAM/` | 16 MB | MAX96717, MAX96714 (plus safety manual), MPQ70165FS, IS25WP01G, DRAM datasheets | Medium to high. Interfaces and configuration |
| `_page_links/` | 144 KB | HTML redirectors so Word links open a PDF at a given page | Keep as is, because Word documents depend on it |

## Findings

1. **The repo is mostly a document archive plus a test framework, with no cybersecurity artefacts yet.** The only cybersecurity content is SRS chapter 23, the architecture elements `UCM_OA` and `CS_APPL_OA`, and the SOW1 interface spec. This workspace fills that gap.
2. **About 90% of the size is the vendored test framework** (`Gitlab Files`): 1,294 DLLs, 103 EXEs, 1,466 `.pyc` files, a virtual environment, and binary tools (`HexXtract_Tool.exe` at 55.7 MB and `avcodec-58.dll` at 89.3 MB exceed GitHub's recommended 50 MB). It works, but it makes clones slow. Consider Git LFS or moving it to its own repo.
3. **Several documents exist in multiple versions** with no marker of which is current: four revisions of the S5K3B6SA datasheet (plus an S5K3B6SX preliminary), two CV22FS HW programming manuals (1.2 and 1.5), five FSR versions (`FSRs NEW`, `_EVEN_NEWER`, `_PREreviewed_v.0.1/0.4`), two TSC versions. Cybersecurity work should cite the version it used. `03_source_index.md` lists the version chosen.
4. **Leftover and local-only files are in the repo**: `.drawio.bkp` and `.dtmp` lock files, `*.bak` result files, `New Text Document.txt`, and a 12.9 MB Outlook `.msg` at the top level. A `.gitignore` for these would help.
5. **Confidential material.** Several documents are customer or supplier internal (Volvo interface spec, Samsung security policy references, Ambarella manuals, Polarion exports). The repository must stay private.
6. **Some referenced documents are not in the repo**: `Security_Policy_REV1.00.pdf` and `CYBERSECURITY_KEY.FUSING_GUIDE.pptx` (Samsung key provisioning, cited in the Volvo interface spec). They are needed to test the SOW1 authentication chain.
7. **The SRS is Draft.** All 249 cybersecurity requirements are Draft, and 52 have open `[X]` parameters. Test design can start, but thresholds cannot be final.

## Not changed

No file was moved, renamed or deleted. If you later want a physical restructuring of the document folders, the risk is the relative links in the Word documents (`_page_links` and the `docx` files in `Analysis/` and `Functional Safety-Development/`). A restructure would need those links rewritten as part of the same change.
