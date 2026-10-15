# Software-level cybersecurity test areas

Software level means the application software tested through its protocol interfaces, mainly Ethernet, with the bench simulating the vehicle ECU. The proposed test IDs become real once you send the feature requirements.

## CS-DTLS: DTLS 1.3 client (SRS 23.1, 90 requirements, 12 sub-areas)

The SRS makes SOW2 the DTLS 1.3 **client** with a pre-shared key and ECDHE. The cipher suite is `TLS_AES_128_GCM_SHA256`. The bench plays the server (vehicle ECU) and is used to send correct and incorrect handshake messages.

| Sub-area (SRS) | Proposed checks |
|---|---|
| 23.1.1 Local preparation: PSK loading, random generation, ephemeral ECDHE | Handshake aborts if the PSK or PSK identity is missing. Client Random is unique for N handshakes. A fresh ECDHE key pair per handshake. Handshake aborts if random generation fails |
| 23.1.2 ClientHello | Only DTLS 1.3 in `supported_versions`. Only supported AEAD suites offered. `key_share` holds the public key and no private key |
| 23.1.3 / 23.1.4 HelloRetryRequest, ServerHello | Server selects an unadvertised suite, wrong version or an invalid public key: handshake terminated and a security-log entry written |
| 23.1.5 to 23.1.8 Secret derivation, EncryptedExtensions, Finished | Corrupt or truncated EncryptedExtensions, wrong Server Finished: handshake terminated |
| 23.1.9 Session establishment | Session only after a valid Finished exchange. Timeout and retransmission limits enforced |
| 23.1.10 Application data: record protection, sequence numbers, anti-replay, record size, freshness | Replayed, reordered, modified and oversize records are dropped. Freshness window is enforced |
| 23.1.11 Fragmentation | Fragment overlaps, missing fragments, out-of-order fragments |
| 23.1.12 Error handling and security logging | Each failure class above produces the specified log event and does not leave a half-open session |

Needs: a scriptable DTLS 1.3 server and fault-injecting peer. This is **not in the repo today**. Options: a patched open-source DTLS stack, or a purpose-built Python peer. See `../04-Test-Environment/cs_bench_gap_analysis.md`.

## CS-SOMEIP: SOME/IP service interface (SRS ch.7)

Existing tests in `Python/TestPool/Ethernet_Comm.-SOMEIP/` already cover: malformed message, unknown service/method ID, wrong interface or protocol version, message type, length and return-code validation, invalid-message flood, `setCamExclusive` lock behaviour and `eraseCamExclusive` when not locked. These are functional robustness tests with security value. They should be **reused and referenced**, and not rewritten. New cybersecurity tests to add:

| Proposed test | What is checked |
|---|---|
| CS-SOMEIP-001 | Control methods (`setCamControl`, `setDataBlock`, `setCamID`) accepted only inside the authenticated session, if the architecture requires that (to confirm) |
| CS-SOMEIP-002 | Exclusivity abuse: a second client tries to release or override `setCamExclusive` |
| CS-SOMEIP-003 | Service-discovery spoofing: a rogue `OfferService`, or subscription to `subscribeRoiVideo` with invalid payload |
| CS-SOMEIP-004 | Fuzzing of header and payload fields beyond the existing validation tests |

## CS-UCM: software download and rollback (SRS 7.4.2)

| Proposed test | What is checked |
|---|---|
| CS-UCM-001 | `TransferStart`/`TransferData`/`TransferExit` with a package that has a wrong size, a bad checksum or truncation. The package is rejected and the running software is unaffected |
| CS-UCM-002 | `ProcessSwPackage` on an unsigned or wrongly signed package is rejected |
| CS-UCM-003 | `Activate`, `Rollback` and `RevertProcessedSwPackages` when the UCM does not permit them: error response with return code `kOperationNotPermitted` (0x05). The SRS specifies this for Rollback (MVC-114902), and the others need checking against SRS 7.4.2.15 and 7.4.2.16 |
| CS-UCM-004 | Interrupted transfer (power cut, `Cancel`, link down) leaves a bootable system |
| CS-UCM-005 | Downgrade to an older valid package is rejected (ties to anti-rollback, SRS 23.4) |

Needs: package-signing toolchain and the UCM message definitions. The SRS already gives verification criteria for each method's response codes.

## CS-NVM: stored data

| Proposed test | What is checked |
|---|---|
| CS-NVM-001 | Corrupted production data block or configuration block is detected on boot, and the specified fallback or safe state is applied (SRS 13, TSR flash/NVM draft) |
| CS-NVM-002 | Security data in flash (`SecurityData` / secure storage) is not readable through the normal software interfaces |

## Dependencies and open decisions

1. 52 SRS requirements still have open `[X]` choices. Test thresholds can only be fixed after those are decided. A list is filterable in the CSV (search `[X]`).
2. DTLS payload scope (control only, or video too) decides whether `CS-DTLS` covers the RTP path.
3. The SRS is in Draft. Re-extract the CSV when a new revision appears. The extraction script is a one-off; I can turn it into a committed tool if you want.
