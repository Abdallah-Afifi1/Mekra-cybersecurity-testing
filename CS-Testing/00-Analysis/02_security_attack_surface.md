# Security attack surface of the MVC (SOW2)

Derived from the architecture export (System Architecture rev. 670544, 2026-08-02), the SRS (rev. 731696, 2026-10-08), the schematics (MVCU01K BOM02K), the CV22FS HW Programming Reference Manual 1.5 and the SOW1 Camera Interface Specification. Where something is my inference and not stated in a document, it says **(to confirm)**.

## Architecture elements that are already cybersecurity-specific

| Element | Source | Meaning |
|---|---|---|
| `UCM_OA` with `ppSecurity` (CSRuntime-SoftwareIF) and `ppFlash` | System Architecture | Update and configuration management (software download). Talks to the security runtime and to the flash |
| `CS_APPL_OA` with `ppSecureStorage`, `ppSecureComm.` | System Architecture | Cybersecurity application: secure storage and secure communication |
| `SecurityData` (CSProgrammable) on flash and on the flash-access port | System Architecture | Security data region in the SPI flash |
| `ppSPIneedleAdapter` and `ppFlashAccess` (SPI) | System Architecture | Physical SPI access to the flash. This is a production or service access path |
| `ProductionData`, `RuntimeData` | System Architecture | Production data block (integrity) and runtime data in NVM |

## Interfaces and what to test

| # | Interface | Evidence | Threat classes | Requirement source | Test area |
|---|---|---|---|---|---|
| 1 | **Ethernet to vehicle ECU** (100/1000BASE-T1, PHY TJA1104A / TJA1121A, RGMII to SoC) | Schematic, architecture `ppEthernet`, SRS ch.5 to 8 | Spoofing, tampering, replay, flooding, malformed input | SRS ch.5 (Ethernet, DHCP client), ch.6, ch.7 (SOME/IP), ch.23.1 (DTLS 1.3) | `CS-DTLS`, `CS-SOMEIP`, `CS-ETH` |
| 2 | **DTLS 1.3 session with the vehicle ECU** (PSK, ECDHE, TLS_AES_128_GCM_SHA256) | SRS 23.1, 90 requirements | Handshake downgrade, replay, key reuse, weak randomness, fragmentation abuse | SRS 23.1.1 to 23.1.12 | `CS-DTLS` |
| 3 | **SOME/IP camera service** (getCamIdentification, setCamControl, setDataBlock, subscribeRoiVideo, etc.) | SRS 7.3 | Unauthenticated control, malformed headers, exclusivity lock abuse, flood | SRS 7.1.3, 7.3.x | `CS-SOMEIP` (existing tests cover header validation and flood) |
| 4 | **Software download and rollback** (UCM: TransferStart, TransferData, TransferExit, ProcessSwPackage, Activate, Rollback, RevertProcessedSwPackages) | SRS 7.4.2 | Unsigned or modified package, downgrade, interrupted update, unauthorised rollback | SRS 7.4.2, 23.4 (boot verification, anti-rollback) | `CS-UCM`, `CS-BOOT` |
| 5 | **GMSL2 link to the SOW1 camera** (MAX96714 deserializer, MAX96717 serializer): I2C tunnel, GPIO forwarding, video | Schematic, SRS ch.15, SOW1 interface spec | Spoofed camera, manipulated I2C configuration, injected frames | SRS 23.2 (57 requirements), ch.20.3 (I2C manipulation use cases) | `CS-SOW1`, `CS-GMSL` |
| 6 | **SOW1 authentication chain**: Samsung Root public key verifies the imager's RSA device key, ECU generates session key plus row selection and sends it RSA-encrypted, imager embeds AES-CMAC in each frame footer (from frame 18 on), signed EEPROM verified with the Bosch public key | SOW1 Camera Interface Spec (Volvo D040574), SRS 23.2 | Counterfeit camera, replayed frames, stale session key, unsigned EEPROM | SRS 23.2.1 to 23.2.7 | `CS-SOW1` |
| 7 | **Debug ports**: `ISP_JTAG` (test points TP1200 to TP1203), the `UART` (APB) and `UART0`/`UART1` nets on the SoC. UART2 and UART3 appear only as alternate functions on SMIO pins | Schematic | Unauthorised debug access, unlock bypass | SRS 23.3 (39 requirements): JTAG locked by default in production, unlock only through UART challenge-response with fresh challenge, nonce, salt and session ID, validity period 30/60/120 s [X] | `CS-DBG` |
| 8 | **External SPI NOR flash** (IS25WP01G-RILA3, `NORSPI_*` nets) and **secure boot** | Schematic, SoC HW PRM section 2 (POC bits, secure boot strap, signed image size field, OTP ROM), SRS 23.4 (35 requirements) | Modified boot image, rollback, flash read-out | SRS 23.4: SHA-256, RSA 2048/3072/4096 [X], public key in OTP, boot stages Safety BST, Safety BLD, Safety OS, A53 BLD, ATF, OS image | `CS-BOOT` |
| 9 | **DRAM** (scrambling AES engine, write-only key register, address translation tables per DRAM client) | SRS 23.5 (28 requirements) | Cold-boot or probing attack, DMA access outside range | SRS 23.5 | `CS-DRAM` |
| 10 | **NVM data blocks** (production data, software configuration, ImVer) | SRS ch.13, architecture | Tampering with production or configuration data | SRS ch.13, 23.4 | `CS-NVM` |
| 11 | **MACsec capability of the PHYs** (TJA1104A, TJA1121A) and **MACsec bench switch** (Technica TE-2004, MKA) | PHY datasheets, bench description | Layer-2 spoofing, unauthorised links | **(to confirm)** whether MACsec is used on this product. No SRS requirement for it was found | `CS-ETH` (only if used) |
| 12 | **Time sync (gPTP) and FSYNC** | SRS ch.9, 10 | Spoofed time master, frame-timing manipulation (also a safety goal) | SRS ch.9, 10 | `CS-ETH` |
| 13 | **Video stream (RTP) and SEI frame tagging** | SRS ch.8, 11 | Stream injection, tag manipulation | SRS ch.8, 11, 23.1 **(to confirm whether the stream is inside DTLS)** | `CS-DTLS` / `CS-ETH` |

## Open points

1. Which traffic runs inside the DTLS session: only control and SOME/IP, or also RTP video? SRS 23.1 says "SOW2 to Vehicle ECU secure communication interface" without naming the payloads.
2. Is MACsec used? Hardware and bench support it, but no requirement was found.
3. ECU lifecycle states (production, development, service). SRS 23.3 refers to "production mode" and a "lifecycle state that permits debug unlock", and the states and their transitions are not defined in the documents I read.
4. Samsung key-provisioning documents (see `01_repo_analysis.md`, finding 6) are missing.
5. 52 SRS requirements still carry open `[X]` parameters. See `03-Traceability/`.
6. DTLS role: the SRS says SOW2 is the DTLS **client**. A vehicle-ECU simulator acting as the DTLS **server** is needed on the bench (see `04-Test-Environment/`).
