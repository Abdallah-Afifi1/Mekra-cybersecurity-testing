# Traceability

| File | Content |
|---|---|
| `SRS-ch23_cybersecurity_requirements.csv` | 249 requirements from SRS chapter 23 (rev. 731696, 2026-10-08), one per row, with section, text, status, the SRS verification criteria, and empty columns for the planned test IDs, level, status and notes |
| `CS_concept_requirements.csv` | 41 system cybersecurity requirements from the Cybersecurity Concept (SOW1 to SOW2 interface, secure debug, hardware protection), with test IDs |
| `TECH-CS_SOW1-SOW2_requirements.csv` | 30 technical cybersecurity requirements for the SOW2 to SOW1 interface, with the concept requirements they satisfy and test IDs |
| `feature_requirements_template.csv` | Same columns for the requirements you will send per feature. Copy it per feature |

## Counts

| Domain | Requirements |
|---|---|
| DTLS 1.3 link, SOW2 to vehicle ECU (23.1) | 90 |
| SOW2 to SOW1 camera authentication and video (23.2) | 57 |
| Secure debug (23.3) | 39 |
| SPI flash secure interface and secure boot (23.4) | 35 |
| DRAM secure interface (23.5) | 28 |
| **Total** | **249** (all Draft) |

- 52 requirements contain an open `[X]` configuration choice.
- 27 requirements have no verification criteria in the SRS.
- Concept-level requirements (Polarion, readyForReview) are in the two other CSV files and are counted in `05-Requirements-Inbox/SecureComm_SOW1-SOW2_and_SecureDebug/README.md`.

## Columns to fill

`CS test case ID(s)` (for example `CS-DBG-001`), `Test level` (System, Software or Component), `Test status` (Not started, Designed, Implemented, Passed, Failed, Blocked), and `Notes` (the decision that is needed, or the bench item that is missing).

## Rule

Requirement text is copied verbatim from the SRS and is not edited here. If the SRS changes, regenerate the requirement columns and keep the test columns.
