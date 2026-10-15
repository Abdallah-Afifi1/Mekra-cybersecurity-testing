# CS-Testing: cybersecurity test workspace (SOW2 Rear & Trailer camera, MEKRA Vision Controller)

Scope: **system and software cybersecurity testing** of the MEKRA Vision Controller (MVC, project 11-P-01467 / 11-E-01405 SOW2).

This workspace was built from the material already in `Components Datasheets/`. **No original file was moved or changed**, because the Word documents link to the datasheets by relative path (see `_page_links/README.md`). Everything here points back to a source document.

## Layout

| Folder | Content |
|---|---|
| `00-Analysis/` | What is in the repo, the attack-surface map, and an index of every source document with its security relevance |
| `01-System/` | System-level test areas: hardware interfaces, debug ports, flash, DRAM, SerDes/camera link, Ethernet |
| `02-Software/` | Software-level test areas: DTLS, SOME/IP, software download (UCM), secure boot, secure storage |
| `03-Traceability/` | Requirement-to-test matrix. Loaded: the 249 SRS chapter 23 requirements, the 41 concept and 30 technical requirements of the first feature |
| `04-Test-Environment/` | What the existing bench can do for cybersecurity tests and what is missing |
| `05-Requirements-Inbox/` | **Drop your per-feature requirements here** (template included) |

## Where things stand

- 249 cybersecurity requirements (SRS chapter 23, SW/HW/Mechanical Requirements rev. 731696, 2026-10-08) are extracted into `03-Traceability/SRS-ch23_cybersecurity_requirements.csv`. All are **Draft**.
- 52 of the 249 still contain open `[X]` configuration choices (for example the RSA key length, the debug-unlock challenge validity of 30, 60 or 120 seconds, and the secure-boot failure action). These need a decision before a test can have a pass/fail threshold.
- 27 of the 249 have no verification criteria in the SRS.
- Feature loaded: **Secure communication SOW1 to SOW2, Secure debug, Hardware security protection** (41 concept requirements and 30 technical requirements from Polarion). 46 test cases are specified in `01-System/` (30 CS-SOW1, 15 CS-DBG, 1 CS-HWP). Findings and blockers: `05-Requirements-Inbox/SecureComm_SOW1-SOW2_and_SecureDebug/README.md`.
- No test scripts exist yet. The existing framework has SOME/IP and DHCP tests that can be reused (`04-Test-Environment/`).

## Next step

Send the requirements for each feature. Put them in `05-Requirements-Inbox/` or paste them in the chat. For each feature I will then add test cases, link them in the traceability matrix, and, once the missing bench items are settled, write the scripts in the existing iTestStudio format.

## Naming

- Test case ID: `CS-<AREA>-<nnn>`, for example `CS-DTLS-001`, `CS-DBG-003`, `CS-BOOT-002`. The areas are DTLS, SOW1, DBG, BOOT, DRAM, SOMEIP, UCM, ETH, GMSL, NVM.
- The test case ID is also the `testcase_id` of a script in the existing framework, which needs a unique ID per script.
