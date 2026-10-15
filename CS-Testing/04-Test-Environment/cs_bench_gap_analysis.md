# Cybersecurity test bench: what exists and what is missing

Sources: `Test environment description/Description_of_test_environment_SOW-2.docx` (v0.1.3), `Analysis/Technica_Bench_Equipment_Capability_Analysis.docx`, `Analysis/Interface - HW Coverage Matrix.docx`, and the framework in `Gitlab Files/…/` (its `CLAUDE.md`). The "needed" column is my assessment for cybersecurity testing and **to confirm** with you.

## Already available

| Item | Use for cybersecurity |
|---|---|
| iTestStudio HIL framework with Python test pool, `ttk_*` libraries, report generation | Run cybersecurity scripts in the same format and reports as the functional tests |
| Python libraries for SOME/IP, service discovery, DHCP server, RTP sniffer, Technica switch control | SOME/IP robustness, DHCP hostile-server tests, traffic analysis |
| 20+ SOME/IP and camera-service test scripts | Reuse as the robustness baseline |
| Technica TE-1177 / TE-2004 (MACsec, MKA) Ethernet switch and capture modules, TE-1190 GMSL capture | Traffic injection, capture, MACsec tests (if used), GMSL observation |
| Wireshark 4.4.9 with Technica dissector | Protocol analysis of DTLS handshakes and SOME/IP |
| Lauterbach (via SoC) | JTAG state checks, register and I2C access, DRAM-range access attempts |
| Saleae Logic 2 | Capture of I2C, UART and SPI lines |
| R&S NGP824 power supply, Siglent DMM, Vötsch climate chamber | Power-cycle and reset tests, interrupted-update tests |

## Missing or to confirm

| Item | Needed for | Status |
|---|---|---|
| Scriptable DTLS 1.3 server and fault-injecting peer (PSK, ECDHE, TLS_AES_128_GCM_SHA256) | CS-DTLS (90 requirements) | **Not in repo.** Build or adopt |
| UART host tool and scripts for the debug unlock service, plus key material | CS-DBG | Not in repo. Unlock protocol details come from SRS 23.3 and the remaining requirement text |
| Defined ECU lifecycle states and a way to switch them on the bench | CS-DBG, CS-BOOT | Open question |
| Image-signing toolchain, keys, OTP/eFuse provisioning procedure | CS-BOOT, CS-UCM | Not in repo |
| SPI flash access through the needle adapter (programmer or clip) and a way to read back the flash | CS-BOOT, CS-NVM | Architecture lists the port. Equipment to confirm |
| SOW1 camera with fused security keys, or a simulator, plus Samsung key documents | CS-SOW1 | **Documents missing** (`Security_Policy_REV1.00.pdf`, `CYBERSECURITY_KEY.FUSING_GUIDE.pptx`) |
| In-line I2C injector (FPGA man-in-the-middle) | CS-GMSL | Listed as **Missing** in the Interface / HW Coverage Matrix |
| Packaging tool for software-update packages | CS-UCM | Not in repo |
| Fuzzing framework for SOME/IP payloads and DTLS records | CS-SOMEIP, CS-DTLS | Not in repo |
| Hardware fault-injection (voltage or clock glitching) | Optional extension of CS-BOOT | Not requested. Only if the SRS or your plan asks for it |

## Practical suggestion

Start with what needs no new hardware: CS-SOMEIP (reuse), CS-ETH, CS-NVM, and the log-checking parts of CS-DTLS using a simple Python DTLS peer. In parallel, close the three blockers with the longest lead time: the lifecycle definition, the signing and key material, and the Samsung key documents.
