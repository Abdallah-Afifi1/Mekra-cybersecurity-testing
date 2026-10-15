# System-level cybersecurity test areas

System level means the integrated MVC on the bench (hardware plus software), tested through its physical interfaces. Test IDs are proposals. They become real once you send the feature requirements. Every row traces to SRS requirements in `../03-Traceability/SRS-ch23_cybersecurity_requirements.csv`.

## CS-DBG: debug access (SRS 23.3, 39 requirements)

| Proposed test | What is checked | Requirement anchors |
|---|---|---|
| CS-DBG-001 | In production mode, after power-on and after reset, JTAG (`ISP_JTAG`, TP1200 to TP1203) does not respond | MVC-107859 |
| CS-DBG-002 | Unlock attempts on any interface other than the dedicated UART service interface are rejected | MVC-107862, MVC-107863 |
| CS-DBG-003 | Challenge request with invalid format, or in a lifecycle state that does not allow it, is rejected | MVC-107865 |
| CS-DBG-004 | Every unlock transaction gets a fresh challenge, nonce, salt and session ID. No value repeats across N transactions | MVC-107864, MVC-107857 |
| CS-DBG-005 | A response with the wrong ECU ID, a stale response after the validity period, or a replayed response is rejected | MVC-107887, MVC-107893 |
| CS-DBG-006 | Brute-force and rate behaviour of the unlock service (lock-out policy, if defined) | to be taken from the remaining 23.3 requirements |

Needs: UART access to the unlock service, JTAG probe (Lauterbach is on the bench), a way to set the lifecycle state, and the key material for the valid unlock path. Open: the lifecycle states (see `../00-Analysis/02_security_attack_surface.md`, open point 3).

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

## CS-GMSL and CS-SOW1: camera link (SRS 23.2, 57 requirements, plus ch.15 and 20.3)

| Proposed test | What is checked |
|---|---|
| CS-SOW1-001 | Authentic imager: the device key chain verifies against the Samsung root public key |
| CS-SOW1-002 | A camera with an unsigned or wrongly signed device key is refused. No session is established (23.2.3, 23.2.7) |
| CS-SOW1-003 | Frames with a wrong, missing or replayed AES-CMAC are rejected after authentication is active. The first 17 frames have no tag by design, so the test must account for this |
| CS-SOW1-004 | A new session key is generated per session and invalidated on reset, expiry or failure (23.2.4, MVC-108158) |
| CS-SOW1-005 | The signed EEPROM read-only data is verified before use. A modified EEPROM is rejected |
| CS-GMSL-001 | Manipulating I2C SerDes data after and during boot (use cases in SRS 20.3.1) is detected or has no security effect |

Needs: a real or emulated SOW1 camera with fused keys, or a camera-side simulator, and the Samsung key-provisioning documents (missing, see `../00-Analysis/01_repo_analysis.md`). The bench has the Technica TE-1190 GMSL capture module and the Lauterbach I2C path, which cover observation but not an in-line manipulator (the coverage matrix lists the I2C injector as Missing).

## CS-ETH: network layer

| Proposed test | What is checked |
|---|---|
| CS-ETH-001 | DHCP client behaviour with hostile servers (wrong options, FORCERENEW without authentication, address changes) |
| CS-ETH-002 | Link-up, flooding and malformed Ethernet frames do not stop video or safety functions |
| CS-ETH-003 | gPTP: messages from a non-master or malformed messages are filtered (SRS 9.1.1) |
| CS-ETH-004 | MACsec on the TJA1104A and TJA1121A: only if the product uses it |

Needs: Technica TE-1177 / TE-2004 for injection and capture, Wireshark with the Technica dissector, the existing DHCP and service-discovery libraries.
