# CS-DBG and CS-HWP: secure debug and hardware protection (16 requirements)

Generated from the Polarion exports in `../05-Requirements-Inbox/SecureComm_SOW1-SOW2_and_SecureDebug/` (baseline "readyForReview"). The procedure and pass criteria are copied **verbatim** from the verification criteria of each requirement, so they stay traceable. The "Equipment" lines are my assessment and need your confirmation. Test status for every case: **Not started**.

Level: system. Source: Cybersecurity Concept sections 2.2.3 Secure Debug (CAL 1) and 2.2.4 Hardware Security Protection (CAL 2). Three debug requirements are verified by **review**, not by test, and are marked below.

## System Cybersecurity Requirements > Secure Debug

### CS-DBG-001: The system shall keep the hardware debug interfaces, including JTAG, locked by default when the ECU operates i…

- **Requirement:** MVC-103061 (2.2.3-1), CAL 1, method: **Test**
- **Full text:** The system shall keep the hardware debug interfaces, including JTAG, locked by default when the ECU operates in locked mode and shall permit debug unlocking through an authorized challenge-response authentication mechanism.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Set the ECU to locked mode and attempt to access the hardware debug interfaces, including JTAG, without completing an authorized challenge-response transaction. The verification passes if the interfaces remain locked by default, failed or unauthorized transactions do not unlock them, and access is enabled only after successful completion of an authorized challenge-response transaction.

### CS-DBG-002: The system shall receive debug-unlock requests through the designated debug service communication interface du…

- **Requirement:** MVC-103060 (2.2.3-2), CAL 1, method: **Test**
- **Full text:** The system shall receive debug-unlock requests through the designated debug service communication interface during runtime and shall keep hardware debug access locked until successful authentication.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Send a valid debug-unlock request through the designated debug service communication interface while the ECU is operating at runtime. The verification passes if the request is received and processed through the designated interface and the hardware debug access remains locked until the authentication process completes successfully.

### CS-DBG-003: The system shall generate a fresh random debug authentication challenge using the platform True Random Number…

- **Requirement:** MVC-103050 (2.2.3-3), CAL 1, method: **Review**
- **Full text:** The system shall generate a fresh random debug authentication challenge using the platform True Random Number Generator (TRNG) after receiving a valid debug unlock request.
- **Equipment (assessment):** Design and code review evidence: software design, call flow, memory map or linker configuration
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Review the software design, implementation, and call flow. The verification passes if the platform TRNG is used as the source for generating a fresh random debug authentication challenge and challenge generation is triggered only after receipt of a valid debug-unlock request.

### CS-DBG-004: The system shall generate a unique debug authentication challenge for each debug unlock request and shall enfo…

- **Requirement:** MVC-103043 (2.2.3-4), CAL 1, method: **Test**
- **Full text:** The system shall generate a unique debug authentication challenge for each debug unlock request and shall enforce a limited challenge validity period defined by the OEM.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Initiate multiple debug-unlock transactions and record the generated challenges. The verification passes if each transaction receives a unique challenge, an otherwise valid response is accepted only within the OEM-defined challenge validity period, and a response received after expiry is rejected.

### CS-DBG-005: The system shall independently compute the expected AES-CMAC value using the derived DebugUnlockSessionKey and…

- **Requirement:** MVC-103047 (2.2.3-6), CAL 1, method: **Review**
- **Full text:** The system shall independently compute the expected AES-CMAC value using the derived DebugUnlockSessionKey and the active debug-unlock transaction context within the secure execution environment upon receiving a debug-unlock response.
- **Equipment (assessment):** Design and code review evidence: software design, call flow, memory map or linker configuration
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Review the software architecture, implementation, and debug-unlock processing flow. The verification passes if, upon receiving a debug-unlock response, the system independently computes the expected AES-CMAC value inside the secure execution environment using the derived DebugUnlockSessionKey and the active debug-unlock transaction context.

### CS-DBG-006: The system shall reject any expired, reused, malformed, invalid, unauthorized, or cryptographically incorrect…

- **Requirement:** MVC-103037 (2.2.3-8), CAL 1, method: **Test**
- **Full text:** The system shall reject any expired, reused, malformed, invalid, unauthorized, or cryptographically incorrect debug unlock response.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Submit separate debug-unlock responses representing expired, reused, malformed, invalid, unauthorized, and cryptographically incorrect cases. The verification passes if every tested response is rejected and the hardware debug interface remains locked.

### CS-DBG-007: The system shall unlock the hardware debug interface only after successful verification of the debug unlock re…

- **Requirement:** MVC-103039 (2.2.3-10), CAL 1, method: **Test**
- **Full text:** The system shall unlock the hardware debug interface only after successful verification of the debug unlock response.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Execute debug-unlock transactions using a successfully verified response and using failed, incomplete, or incorrect responses. The verification passes if the hardware debug interface is unlocked only after successful verification of the debug-unlock response and remains locked in all other cases.

### CS-DBG-008: The system shall derive a debug unlock session key using a CMAC Key Derivation Function (KDF)

- **Requirement:** MVC-105883 (2.2.3-11), CAL 1, method: **Test**
- **Full text:** The system shall derive a debug unlock session key using a CMAC Key Derivation Function (KDF)
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Derive a DebugUnlockSessionKey using defined test inputs and compare the generated key against the output of an approved reference CMAC Key Derivation Function. The verification passes if the derived key matches the expected CMAC-KDF output for all tested input sets.

### CS-DBG-009: The system shall store the derived debug unlock session key only in the DRAM.

- **Requirement:** MVC-105881 (2.2.3-12), CAL 1, method: **Review**
- **Full text:** The system shall store the derived debug unlock session key only in the DRAM.
- **Equipment (assessment):** Design and code review evidence: software design, call flow, memory map or linker configuration
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Review the memory architecture, memory map, linker configuration, and key-handling implementation. The verification passes if the derived DebugUnlockSessionKey is stored only in its designated DRAM location and no copy of the key is stored in non-DRAM or persistent memory.

### CS-DBG-010: The system shall securely erase the derived debug unlock session key, and intermediate cryptographic material…

- **Requirement:** MVC-105887 (2.2.3-13), CAL 1, method: **Test**
- **Full text:** The system shall securely erase the derived debug unlock session key, and intermediate cryptographic material from the DRAM after completion of the debug session, upon session termination, or upon authentication failure.
- **Equipment (assessment):** Lauterbach DRAM inspection, UART service host
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Generate a DebugUnlockSessionKey and intermediate cryptographic material, then separately trigger debug-session completion, session termination, and authentication failure. The verification passes if inspection of the allocated DRAM locations after each trigger confirms that the derived key and intermediate cryptographic material are no longer recoverable.

### CS-DBG-011: The system shall permit debug access only for an authorized and time-limited debug session and shall automatic…

- **Requirement:** MVC-103038 (2.2.3-14), CAL 1, method: **Test**
- **Full text:** The system shall permit debug access only for an authorized and time-limited debug session and shall automatically relock the debug interface after session timeout, Power-On Reset (POR), completion of debug activities, lifecycle transition, or detection of security violations.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Complete an authorized debug-unlock transaction and verify that debug access is available only during the authorized, time-limited session. Separately trigger session timeout, Power-On Reset, completion of debug activities, lifecycle transition, and detection of a security violation. The verification passes if the hardware debug interface automatically relocks after every specified trigger and unauthorized access is not permitted.

### CS-DBG-012: The system shall limit repeated failed debug authentication attempts and temporarily block further attempts af…

- **Requirement:** MVC-103049 (2.2.3-15), CAL 1, method: **Test**
- **Full text:** The system shall limit repeated failed debug authentication attempts and temporarily block further attempts after a configurable threshold is reached.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Perform consecutive failed debug-authentication attempts using the configured failure threshold. The verification passes if further authentication attempts are temporarily blocked when the threshold is reached, attempts during the blocking period are rejected, and new attempts are permitted only after the configured temporary blocking period expires.

### CS-DBG-013: The system shall minimize information returned during failed authentication attempts to avoid disclosure of au…

- **Requirement:** MVC-103048 (2.2.3-16), CAL 1, method: **Test**
- **Full text:** The system shall minimize information returned during failed authentication attempts to avoid disclosure of authentication status or cryptographic verification details.
- **Equipment (assessment):** UART service host with a valid and an invalid debug-unlock client, JTAG probe (Lauterbach), ECU lifecycle control
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Generate different failed authentication conditions and monitor all externally observable responses. The verification passes if the returned information is limited to the defined generic failure information and does not disclose the specific authentication failure cause, expected cryptographic values, received cryptographic values, or internal verification details.

### CS-DBG-014: The system shall log all debug unlock activities, including unlock requests, challenge generation events, succ…

- **Requirement:** MVC-103032 (2.2.3-17), CAL 1, method: **Test**
- **Full text:** The system shall log all debug unlock activities, including unlock requests, challenge generation events, successful unlocks, failed authentication attempts, lockout events, relock events, timestamps, ECU identity, and authentication results.
- **Equipment (assessment):** Authorised log-access mechanism, UART or debug service host, JTAG probe (Lauterbach)
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Trigger a debug-unlock request, challenge generation, successful unlock, failed authentication, lockout, and relock. Retrieve the logs through the authorized log-access mechanism. The verification passes if every triggered event produces a corresponding log entry containing the applicable event type, timestamp, ECU identity, and authentication result without recording secret cryptographic material.

### CS-DBG-015: The system shall restrict access to debug authentication logs to authorized personnel and authorized debug ses…

- **Requirement:** MVC-103027 (2.2.3-18), CAL 1, method: **Test**
- **Full text:** The system shall restrict access to debug authentication logs to authorized personnel and authorized debug sessions only.
- **Equipment (assessment):** Authorised log-access mechanism, UART or debug service host, JTAG probe (Lauterbach)
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Attempt to access the debug authentication logs using: an authorized person during an authorized debug session, an unauthorized person, and an authorized person without an authorized debug session. The verification passes if log access is granted only to the authorized person during the authorized debug session and is denied in all other tested cases.

## System Cybersecurity Requirements > Hardware Security Protection

### CS-HWP-001: The ECU shall protect hardware interfaces, control functions and firmware against unauthorized external access…

- **Requirement:** MVC-116572 (2.2.4-1), CAL 2, method: **Test**
- **Full text:** The ECU shall protect hardware interfaces, control functions and firmware against unauthorized external access and manipulation.
- **Equipment (assessment):** Access to hardware interfaces, reset and power control, firmware update/flash path
- **Procedure and pass criteria (verbatim from the concept's verification criteria):**
  - Verify that unauthorized external access attempts to hardware interfaces are prevented or rejected.
  - Verify that unauthorized external attempts to disrupt hardware functions, including reset or power control functions, do not cause unintended disruption of ECU operation.
  - Verify that unauthorized external attempts to access, modify, or replace ECU firmware are prevented and do not result in execution of unauthorized firmware.

