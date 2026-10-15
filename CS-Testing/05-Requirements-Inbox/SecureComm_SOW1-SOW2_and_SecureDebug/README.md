# Feature: Secure communication SOW1 to SOW2, Secure debug, Hardware security protection

Source: two Polarion exports, baseline "readyForReview" (project 11_P_01467_MEKRA_Vision_Controller). Original files are in this folder unchanged.

| Workbook | Content | Requirements |
|---|---|---|
| `BL_SecureCommunication_SOW1_SOW2_readyForReview_CS_CONCEPT.xlsx` | Cybersecurity Concept (MVC-99199), system cybersecurity requirements | 41 (26 at CAL 2, 15 at CAL 1). 38 verified by test, 3 by review |
| `BL_SecureCommunication_SOW1_SOW2_readyForReview__TECH_CS_CONCEPT.xlsx` | Technical Cybersecurity Concept (MVC-99200), technical requirements for the SOW2 to SOW1 interface | 30 (all CAL 2, all verified by test) |

## What was produced

| Output | Location |
|---|---|
| Concept requirements as CSV with test ID mapping | `../../03-Traceability/CS_concept_requirements.csv` |
| Technical requirements as CSV with "satisfies" links and test IDs | `../../03-Traceability/TECH-CS_SOW1-SOW2_requirements.csv` |
| 30 test cases CS-SOW1-001 to 030 | `../../01-System/CS-SOW1_secure_communication_tests.md` |
| 16 test cases CS-DBG-001 to 015 and CS-HWP-001 (3 of the debug ones are review items) | `../../01-System/CS-DBG_secure_debug_and_hw_protection_tests.md` |

How the structure maps: the 25 system requirements about the SOW1 interface are satisfied by the 30 technical requirements, so tests are written at the technical level (CS-SOW1-xxx) and the system requirements show "covered by". Secure debug and hardware protection have no technical requirements in these files, so they get their own tests directly.

The procedure and pass criteria in the specs are the verification criteria from the workbooks, copied verbatim. I did not rewrite them.

## Findings in the requirements (for you to confirm or fix in Polarion)

1. **Authentication retry count is ambiguous.** MVC-106566 says retransmit the authentication request "up to three times" (that is up to 4 requests in total). MVC-106569 says terminate "after three authentication attempts" (3 requests in total). A test that counts requests on the I2C bus (CS-SOW1-005, CS-SOW1-006) needs one number. The session-establishment pair (MVC-106567 and MVC-106581) says "three retries" in both places and is consistent.
2. **MVC-107641** (use RSASSA-PSS with SHA-256) has no technical requirement linked to it. MVC-106563 verifies exactly this, so the link is probably missing.
3. **Debug requirement numbers skip 2.2.3-5, -7 and -9.** The export has 15 requirements numbered 1 to 18 without those three. Either they were deleted, or they were left out of the export. If they exist, they are not covered here.
4. **Small text problems**: the verification criteria of MVC-106563 number the steps 1, 2, 4, 5 (step 3 is missing), and the requirement text has the typo "whith".
5. **Review items.** MVC-103050 (challenge from the platform TRNG), MVC-103047 (AES-CMAC computed in the secure execution environment) and MVC-105881 (debug session key only in DRAM) are verified by review. Their evidence has to come from the software team, not from a bench test.
6. **Parameters left to the OEM or to configuration** are not given in the concept and are needed for pass/fail: the debug challenge validity period, the failed-attempt threshold, the temporary blocking period, the debug session timeout, and the "defined generic failure information" format. Several SRS 23.3 requirements still have these as `[X]`.

## Blockers for running the tests

1. **Test root key.** CS-SOW1-001 and 003 need a signature made with "the private key corresponding to the trusted Samsung Root Public Key". Only Samsung holds that key. Testing authentication with valid and modified data therefore needs a development configuration with a **test root key** (in OTP or an equivalent store) and an imager or emulator that signs with it. How to do that has to come from the Samsung key documents, which are not in the repo.
2. **A controllable SOW1 responder.** Many cases need to withhold, modify, truncate or delay the imager's responses. A real imager cannot do that. The coverage matrix lists the in-line I2C injector as Missing.
3. **Test frames with known CMAC and counters** for CS-SOW1-019 to 026, plus an independent reference AES-CMAC calculator.
4. **UART debug-unlock host** and a defined ECU lifecycle for CS-DBG.

## Not yet done

- Mapping these concept requirements to the SRS chapter 23.2 (57 requirements) and 23.3 (39 requirements). The SRS items are the software realisation of this concept and should be linked.
- Test scripts. They depend on the blockers above.
