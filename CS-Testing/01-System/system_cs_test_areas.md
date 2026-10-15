# System-level cybersecurity test areas

System level means the integrated MVC on the bench (hardware plus software), tested through its physical interfaces. Test IDs are proposals. They become real once you send the feature requirements. Every row traces to SRS requirements in `../03-Traceability/SRS-ch23_cybersecurity_requirements.csv`.

## CS-DBG: debug access

**Detailed test specs now exist:** `CS-DBG_secure_debug_and_hw_protection_tests.md` (15 secure-debug requirements plus 1 hardware-protection requirement, from your Cybersecurity Concept). The SRS chapter 23.3 has 39 software requirements for the same area. They are more detailed (UART service interface, KDF inputs, validity period 30/60/120 s `[X]`, rejection of unlock attempts on other interfaces). They are not yet mapped to the concept requirements, and some SRS checks have no concept counterpart, for example: unlock attempts through any interface other than the dedicated UART service, and uniqueness of challenge, nonce, salt and session ID across many transactions (MVC-107862, MVC-107864, MVC-107857). These should become extra steps or extra cases once the mapping is done.

Open: the lifecycle states (see `../00-Analysis/02_security_attack_surface.md`, open point 3).

## CS-BOOT: secure boot and flash (SRS 23.4, 35 requirements)

| Proposed test | What is checked | Requirement anchors |
|---|---|---|
| CS-BOOT-001 | Genuine signed images boot. Each stage (Safety BST, Safety BLD, Safety OS, A53 BLD, ATF, OS image) is verified | MVC-107902, MVC-107901 |
| CS-BOOT-002 | An image with one flipped bit is rejected and the configured failure action occurs (halt, reset, recovery or safe state) | MVC-107926, MVC-107924 |
| CS-BOOT-003 | An image signed with a wrong key, a wrong RSA scheme or a wrong key length is rejected | MVC-107906, MVC-107909 |
| CS-BOOT-004 | An older, correctly signed image is rejected (anti-rollback) | MVC-107928 |
| CS-BOOT-005 | Corrupt or missing authenticated metadata (image ID, length, version, stage ID, digest) is rejected | MVC-107921 |
| CS-BOOT-006 | The secure-boot error reporting policy is followed: no external detail, or a secure diagnostic event only | MVC-107930 |
| CS-BOOT-007 | The SoC secure-boot strap and OTP state match the production policy (HW PRM section 2.2) | SoC HW PRM 1.5 |

Needs: the flash access path (`ppSPIneedleAdapter` / `ppFlashAccess`), the image-signing toolchain and keys, OTP programming rules. Open: RSA key length and signature scheme (still `[X]`).

## CS-DRAM: memory protection (SRS 23.5, 28 requirements)

| Proposed test | What is checked | Requirement anchors |
|---|---|---|
| CS-DRAM-001 | Scrambling is enabled in production and disabled only in development builds | MVC-107937 |
| CS-DRAM-002 | No software path reads back the key from the write-only register | MVC-107935 |
| CS-DRAM-003 | A DMA-capable client accessing outside its range is blocked and the configured violation action occurs | MVC-107954, MVC-107953 |
| CS-DRAM-004 | Ranges are configured before DMA clients are enabled | MVC-107960 |

Needs: Lauterbach with SoC access to attempt the cross-range accesses.

## CS-SOW1 and CS-GMSL: camera link

**Detailed test specs now exist:** `CS-SOW1_secure_communication_tests.md` (30 cases, from the Technical Cybersecurity Concept): root key in OTP, device authentication, row information, session key sharing, frame authentication with AES-CMAC and freshness window, protected control commands. The SRS chapter 23.2 has 57 software requirements for the same area, not yet mapped.

Still open at system level, not covered by those 30 cases:

| Check | Source |
|---|---|
| The signed EEPROM read-only data is verified before use. A modified EEPROM is rejected | SOW1 interface spec, SRS 23.2 |
| Manipulating I2C SerDes data after and during boot is detected or has no security effect | SRS 20.3.1 (use cases), no concept requirement found |

Needs: a controllable SOW1 responder or a real camera with known keys. The Samsung key-provisioning documents are missing (see `../00-Analysis/01_repo_analysis.md`). The bench has the Technica TE-1190 GMSL capture module and the Lauterbach I2C path, which cover observation. An in-line manipulator is listed as Missing in the Interface / HW Coverage Matrix.

## CS-ETH: network layer

| Proposed test | What is checked |
|---|---|
| CS-ETH-001 | DHCP client behaviour with hostile servers (wrong options, FORCERENEW without authentication, address changes) |
| CS-ETH-002 | Link-up, flooding and malformed Ethernet frames do not stop video or safety functions |
| CS-ETH-003 | gPTP: messages from a non-master or malformed messages are filtered (SRS 9.1.1) |
| CS-ETH-004 | MACsec on the TJA1104A and TJA1121A: only if the product uses it |

Needs: Technica TE-1177 / TE-2004 for injection and capture, Wireshark with the Technica dissector, the existing DHCP and service-discovery libraries.
