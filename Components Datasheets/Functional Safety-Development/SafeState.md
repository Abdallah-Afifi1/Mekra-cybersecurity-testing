
# SOW2 Safe State

Updated 2026-02-19.

This markdown proposes FSRs and TSRs in order to clarify and specify the Safe State and its mechanism for SOW2.

## Introduction (no specification - informative only)

We recall from the FSC:
- SG1 addresses frame delay > 50 ms within SOW2.
- SG2 addresses frame repetitions >= N (=2 frozen video stream) by SOW2.
- SG3 addresses deterioration of contrast and/or brightness by image processing of SOW2.
- SG4 addresses integrity of critical 'VideoStreamConfiguration' (which includes interfacing responsibility with SOW1 and vehicle)
- SOW1 requires SOW2 to detect interface-related faults

The technical approach includes specific detection measures for each SG:
- (SG1)
  - R52 shall monitor the time per frame from SOW2 input to output.
- (SG2)
  - R52 shall verify the strict monotonicity of the frame numbers from SOW1 and
  - R52 shall monitor the number of repetitions per frame within SOW2.
- (SG3)
  - VIN(`?`) shall verify the integrity of the received images from SOW1.
  - R52 shall verify the 'fault free' configuration of RAWVideoStream in SOW1.
  - R52 shall evaluate the deterioration of contrast and/or brightness by image processing of SOW2 using test-stripes.
  - `???` shall verify the 'fault free' reception of 'VideoStreamConfiguration' from the User/Vehicle.
- (SG4)
  - R52 shall verify the integrity of critical 'VideoStreamConfiguration' at startup and
  - R52 shall verify the correctness and integrity of changed critical 'VideoStreamConfiguration' (both includes interfacing responsibility with SOW1 and ETH).
- (SOW1)
  - `???` shall verify the 'fault free' reception ofthe 'fault free' reception of SOW1.
  
(There are many more TSRs, which are not listed here.)

Technically, the SOW2 Safe State (halted image transmission) can be achieved by one of the mechanisms:
1. R52 stops the sending activity of the PHY (`???`: by command to the PHY or by instrumenting the PMIC to unpower the PHY), or
2. PMIC MPQ70165FS (aka 'the second PMIC') unpowers(QM)/resets(ASIL-B) the SoC.

### PMIC introduction

Among others, SOW2 comprises two Power-Management-ICs (PMICs), which are intended to monitor and manage input voltages and provide their managed voltages as input voltages to the hardware components to the board. Each PMIC can be configured to output a Power Good (PG) signal (high) to indicate that its output voltage looks fine according to the configured monitoring criteria. When a PMIC detects a critical problem, its PG signal is automatically unset (low).

The first PMIC is an MPQ4572GQB. It provides voltage to the Ethernet PHY and to the second PMIC. The PG signal of the first PMIC is used as Power Enable command to the second PMIC. So, the second PMIC will be disabled if the first PMIC unsets its PG signal (to low).

The second PMIC is an MPQ70165FS. It provides voltage to the other components on the SOW2 board, in particular to the System on Chip (SoC) which includes the image processing and stream generation together with a lockstep-core to manage the functional safety for the SoC. The PG signal of the second PMIC and the SoC are wired in such a way that a PG unset (to low) of the second PMIC triggers a reset of the SoC.

The second PMIC is to be configured for ERRIN [MVC-95649] implying Question-Answer-Mode for its Watchdog.

An unpowering of the SoC (and the PHY) can be initiated by both PMICs, but only with QM reliability (cf. System_TSR_1 and System_TSR_2 in Safety Manual of MPQ70165FS). That safety PMIC can only indicate its Safety Error by pulling its PG pin and its ALERT pin to low.

Currently the PCB is planned such that, a low PG or a low ALERT pin triggers a power-reset of the SoC. **Hence, 

In turn, the SoC is wired back to the second PMIC so that the SoC can also trigger a reset:
a) Actively, when the SoC sets (should be change from high to low from SoC) the ERRIN pin (receives this inverted as change from low to high) of the second PMIC (triggering the deep safe state of the second PMIC including a PMIC-induced reset)
b) Passively, when the SoC fails to provide the right answers in the right time (via PMbus) to the Watchdog of the second PMIC.


## Safe State FSRs (Specification)

If not stated otherwise, each TSR in this document section is required with the highest ASIL among SOW2 (currently ASIL-B).

In the following TSRs the "second PMIC" means the PMIC MPQ70165FS.

### FSR - Safe State Definition

While in Safe State, SOW2 shall not transmit any image data via its ethernet interface (i.e., the PHY).

Note: Phenomenologically, the Safe State is defined as halted image transmission [MVC-90277].

Note: While SOW2 is not streaming, it can be considered safe by definition.

### FSR - Transition to the Safe State

When SOW1 indicates a Safety Error to SOW2, then SOW2 shall establish the Safe State within 150 ms.

(Redundant?)When a situation requires transition to the Safe State due to an FSR of SOW2, then SOW2 shall establish the Safe State within the duration required by that FSR.

Note: This subsection can be collectively addressed by saying when "a transition to the Safe State is indicated by an FSR of SOW2".

### FSR - Safe State Persistenece and Exit

If SOW2 has established the Safe State, it shall stay in the Safe State as long as "a transition to the Safe State is indicated by an FSR of SOW2".

The SOW2 System Specification may require a mechanism ("ASIL-QM") to transition back to normal operation [MVC-90280]. If it does so, the design of that mechanism shall ensure (ASIL-B) that any Safe State mechanism of SOW2 will overrule this mechanism.  

### FSR - Verifiability of the Safe State

SOW2 should possess an outbound pin, that indicates while SOW2 is powered on, whether it is in Safe State or not. Otherwise it might be hard for an integrator to verify if SOW2 establishes the Safe State as required.

Note: If such a pin is used, remember to update the TSRs so that this pin is set to indicate the safe state.

Note: The pin could be specified to express "high" when the system is powered on and when the safe state is NOT established; else "low" (i.e., when safe state is establishe or power is down).

### FSR - Diagnosis

Note: Up to now, SOW2 doesn't seem to possess a outbound pin to signal its safe state. When it does, a TSR should require that this pin is set respectively.

Note: The ability of SOW2 to express its Safe State via Ethernet depends on the operability of the PHY and the SoC. So, even if such a diagnostic message is defined, it cannot serve as Safe State indicator.

## Safe State TSRs (Specification)

### Safe State mechanism

Technically, SOW2 shall establish the Safe State by stopping the image sending activity of the PHY.

When "a transition to the Safe State is indicated by an FSR of SOW2", the image sending activity of the PHY shall be stopped through at least one of the following SOW2 components:
1. the SoC (`???`: by command to the PHY directly or indirectly by instrumenting the second PMIC to unpower the PHY), or
2. the second PMIC (by reset of the SoC).

(SoC-Architecture note:) The mechanism 1. shall be under control of the Safety-Core of the SoC (i.e., the Cortex-R52), because the Application-Core is only "ASIL-QM".

### PMIC Responsibility

#### PMIC Voltage control

While SOW2 is powered on, the second PMIC shall ensure that the SoC is powered as required by the provided SoC documentation.

(Under the assumption that the second PMIC was properly configured and started)
When the second PMIC detects a violation of its TSRs 'System_TSR_1' or 'System_TSR_2' (see [PMIC-FSM]), then the PMIC shall establish the Safe State by stopping the SoC within 50 ms.

Note: Since the DRAM controller and the ETH-MAC are part of the SoC, it is expected that the PHY cannot send image data under this circumstance. So the image sending activity of the PHY is indeed stopped.

#### PMIC Watchdog for SoC

The second PMIC shall recurrently check if the Safety-Core of the SoC (i.e., the Cortex-R52) shows unsafe behaviour by expecting the Safety-Core to 'feed' the Watchdog of the PMIC in the configured time and manner.

As implied by [MVC-95649] (which should be ASIL-B), the correct manner is the Question-Answer-Mode (QA-mode). 

The Safety-Core of the SoC shall configure and enable the second PMIC's watchdog, before the SOW2 sends any image data via the PHY.

After the second PMIC's watchdog has been configured, the second PMIC shall reset the SoC whenever the SoC
- responds with the wrong answer or 
- responds later than `???` ms after the last correct response.
The reset shall occur within 50 ms after one of the above conditions became true.

### SoC Responsibility

#### SoC intern

When a safety-relevant sub-component of the SoC indicates a Safety Error to the Safety-Core, the SoC shall establish the Safe State within 200`?` ms by stopping the image sending activity of the PHY (`???`: by command to the PHY directly or indirectly by instrumenting the second PMIC to unpower the PHY).

#### SoC extern

When an OSR Component (see below) indicates a Safety Error to the SoC, the SoC shall establish the Safe State within 200`?` ms by stopping the image sending activity of the PHY (`???`: by command to the PHY directly or indirectly by instrumenting the second PMIC to unpower the PHY).

The following components are technically considered as 'other' safety-relevant components of SOW2 (OSR Components):
- the PMIC (via its PG and ALERT signals)
- the PHY (only if the SoC responsibility is implemented by commanding the PHY)
- the Deserializer (maybe, because VIN of SoC could check Video signals and Safety-Core of SoC could check sensor register settings)

## Open Points

- With the current (B-Sample) design of the SOW2 hardware, the system could not recover itself from Safe State after a reset by the Watchdog of the second PMIC. The reason is a reset loop due to the current wiring logic.

- When the second PMIC (MPQ70165FS) has an OV or UV failure (cf. 'System_TSR_1' or 'System_TSR_2' in [PMIC-FSM]), then it can only guarantee for siganlling the failure by unsetting PG and giving ALERT with ASIL-B, but it can only shut off its output rails with "ASIL-QM". SoC receives this PG/ALERT at POR-L pin, but under the circumstance of OV/UV.

## Referenced Documents

[PMIC-FSM] <https://erg-polarion-p1.mekra.net/polarion/svnwebclient/fileContent.jsp?url=Intern%2F11_P_01467_MEKRA_Vision_Controller%2FProject%20Files%2F02%20Development%2FDatasheets%2FPMIC%2FMPQ70165FS%20Safety%20Manual%20-%20Published%20Datasheet%20%28MPS%20Rev%23%7B3%7D%200.3%29%20%28002%29.pdf>