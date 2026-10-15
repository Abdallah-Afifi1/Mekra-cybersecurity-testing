# Source index (paths relative to `Components Datasheets/`)

Use the **Version used** column when citing a source in a test case.

## Requirements and architecture

| Document | Path | Version used | Security use |
|---|---|---|---|
| Software Requirements (SRS) | `SSRs/11-P-01467_MVC_MEKRA_Vision_Controller_50_SW_HW_Mechanical_Requirements_Software_Requirement.pdf` | rev. 731696, 2026-10-08 | **Chapter 23**, plus ch.5 to 13, 15, 20 |
| System Architecture | `System Architecture/…30_System_Architecture_System_Architecture.pdf` | rev. 670544, 2026-08-02 | UCM, CS_APPL, SecurityData, flash access |
| Internal SoC Architecture | `System Architecture/…40_System_Allocation_Requirements_Internal_SoC_Architecture.pdf` | n/a | SoC allocation |
| Technical Safety Concept | `TSRs/…Technical_Safety_Concept (3).pdf` | n/a | Safe-state reactions to security failures |
| Estimated TSC, FSRs, Functional Safety Concept | `Functional Safety-Development/` | newest of several drafts | Where a security failure leads to a safe state |
| DFA / FTA | `Functional Safety-Development/Work Products/System/` | v0.1 / v0.5 | Dependent-failure and fault-tree inputs |
| SOW1 Camera Interface Spec (Volvo D040574) | `Functional Safety-Development/SOW1 requirements on SOW2/` | v1 | **SOW1 authentication scheme** |
| Volvo ECU requirement spec | `Functional Safety-Development/SOW1 requirements on SOW2/CH3SVC_VT_ECU_RS_18v0_20260702.pdf` | 18v0 (newer than the preliminary 17v2) | Vehicle ECU side requirements |
| Volvo safety questions | `…/VT_CH3_SafetyQuestions_20260618_ML_IMP.xlsx` | 2026-06-18 | Open questions |

## Hardware

| Part | Path | Security use |
|---|---|---|
| Ambarella CV22FS (SoC) | `SoC (CV22FS)/` (HW PRM **1.5** preferred over 1.2, datasheet CV22FS85 **1.4**) | POC and secure boot strap, OTP, JTAG, UART |
| Schematics MVCU01K BOM02K | `Schematics/Schematic Prints_MVCU01K_BOM02K.PDF` | Debug nets, test points, NOR flash, PHYs |
| MAX96714 deserializer | `Deserializer/deserializer_max96714.pdf`, safety manual, `MAX96714_FuSa_TestAccess_and_Register_Reference.docx` | I2C, GPIO forwarding, error indicators |
| MAX96717 serializer | `Serializer/serializer_max96717.pdf` | Remote configuration |
| Samsung S5K3B6SA / SX | `SOW1/` (datasheet **1.0** preferred, older revisions are drafts), `Imager Settings/`, `S5K3B6SA_Embedded_list_wRegisterinfo_Bosch_v0.5.xlsx` | OTP key, CMAC settings, embedded data |
| PHYs | `PHYs/TJA1104`, `PHYs/TJA1121` (incl. MACsec core UM), `PHYs/LAN887x` | MACsec, register access, link-up timing |
| Flash IS25WP01G | `Flash/` | SPI NOR |
| DRAM | `DRAM/` | Memory device |
| PMIC MPQ70165FS | `PMIC/` | Power; relevant to fault-injection tests |

## Test environment

| Document | Path |
|---|---|
| Description of test environment SOW-2 v0.1.3 | `Test environment description/` |
| Bench equipment capability, interface/HW coverage matrix, FuSa validation, TSR read/write analysis, register map index | `Analysis/*.docx` |
| Test framework (HIL project, Python test pool, libraries) | `Gitlab Files/11_p_01467_mekra_vision_controller-main/` (its own `CLAUDE.md` describes how it runs) |
| Equipment manuals (Technica, R&S, Siglent, Vötsch, iTestStudio) | `Gitlab Files/…/Documentation/` |
| Past test reports | `Gitlab Files/…/TestReports/` |

## Cross-reference helpers

| Document | Path |
|---|---|
| PDF page links | `_page_links/` |
| Register map index | `Analysis/Register_Map_Index.docx` |
