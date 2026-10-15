# TSRs related to NVM

>**ATTENTION:** This is just an unreviewed and unreleased draft state of the Flash TSRs, last updated 2026-01-14.

The SOW2 includes a Flash memory as NVM.

>"Everything which needs to saved to be non volatile must be located on the SPI-flash. There is no different Storage for NVM." (Section [NVM](https://erg-polarion-p1.mekra.net/polarion/#/project/11_P_01467_MEKRA_Vision_Controller/wiki/40_System_Allocation_Requirements/System_Allocation_Requirements_SW?selection=MVC-92358&revision=592205) in System_Allocation_Requirements_SW of the *C1-Sample_Design-Freeze_conditional_release_2*)

**ATTENTION:** The SoC includes a kind of BootROM (aka VROM), which also belongs to the class of NVM!.


For the planned NVM allocation, see subsection [Usage of Storage](https://erg-polarion-p1.mekra.net/polarion/#/project/11_P_01467_MEKRA_Vision_Controller/wiki/40_System_Allocation_Requirements/System_Allocation_Requirements_SW?selection=MVC-94554) in System_Allocation_Requirements_SW.

According to `Schematic Prints_MVCU01H_BOM03H.PDF`, the selected Flash module is an ISSI **IS25WP01G-RILA3** ([Data Sheet](https://erg-polarion-p1.mekra.net/polarion/svnwebclient/fileContent.jsp?url=Intern%2F11_P_01467_MEKRA_Vision_Controller%2FProject%20Files%2F02%20Development%2FDatasheets%2FFlash%2FIS25LP_WP_01G-1568422.pdf)).

>Note: See "11. ORDERING INFORMATION – Valid Part Numbers" in Data Sheet for a legend on the product markings. Please, note especially the ones on the temperature range.

According to MRekas, a Failures-In-Time (FIT) calculation for the *base FITs* of the flash is available under [BaseFIT_Flash](https://erg-polarion-p1.mekra.net/polarion/svnwebclient/fileContent.jsp?url=Intern%2F11_P_01467_MEKRA_Vision_Controller%2FProject%20Files%2F02%20Development%2FDatasheets%2FFlash%2FIS25WP01G-RILA3%28FMD257B0%20stack%204%20die%29_1%23pin%29.xlsx). The term "base FIT" means that additional factors, like high temperature are not yet considered, why we should expect the actual FITs higher than the ones in the document.  
On the other hand, 9.4.2.1 in ISO 26262-5:2018 does not require the application of the PMHF method (or the EEC method) to evaluate the residual risk of violating a safety goal. The recommending character of 9.4.2.1 for ASIL-B will be taken into account by an estimate.

## Relevant FSGs/FSRs and criticality

The NVM isn't directly responsible to implement a certain FSR. But, since most program code and start-up configuration data is kept in NVM, the NVM is indirectly relevant to each FSR depending on code or data from NVM.

>Links:
>- [Safety Goals](https://erg-polarion-p1.mekra.net/polarion/#/project/11_P_01467_MEKRA_Vision_Controller/wiki/11_Stakeholder_Requirements/Safety_Goals)
>- [Functional Safety Concept](https://erg-polarion-p1.mekra.net/polarion/#/project/11_P_01467_MEKRA_Vision_Controller/wiki/11_Stakeholder_Requirements/Functional_Safety_Concept)

Depending on the particular SG, the associated criticality is ASIL-B or ASIL-A.

>Comment (CK): I would implement measure(s) sufficient for ASIL-B and use them also for ASIL-A.

## Potential causes for code/data corruption in NVM

* Environmental influences (EMI, radiation, temperature extremes)
* Memory wear and tear
* Latent faults (e.g. bit flips)
* Faulty programming or accidental overwrites
* Improper power supply (e.g., power drop during writing)

### ... and potential measures

* Environmental influences: proper casing and insulation (optional/QM)
* Memory wear and tear: CRC comparison (maybe after copying into RAM?) (ASIL-B)
* Latent faults: CRC comparison (maybe after copying into RAM?) (ASIL-B)
* Faulty programming or accidental overwrites: Verification after flashing (ASIL-B); Programming of the Flash-write protection (maybe region-specific "Password Protection Mode") (QM only, because CRC-32 is very likely to detect random overwrites during runtime and also Flash is not ASIL-qualified)
* Improper power supply (e.g., power drop during writing): (ASIL-B) how about power control by reliable PMIC? Alternatively, an additional checksum over more pages.

## Use cases involving the NVM

0. **Flashing** use case: Copying firmware (including code & data) into the NVM (in production or maintenance workshop)
1. **Startup** use case: Reading code & data from the NVM to perform startup (a special case of **Reading** use case, as it covers a lot of information to be verified in a short time)
2. **Storing** use case: Storing runtime-data into the NVM to persist them
3. **Reading** use case: Reading selected data from the NVM (mainly after startup). (Note: Maybe "Reading" from NVM after startup is not a relevant use case if all data is copied to RAM initially. Then data can be read from ECC-protected RAM. Here we still need to take into account the connection between RAM and SoC).

4. **Power Supply** is relevant for all NVM use cases.

## Concept draft

0. **(Definition)** In the following, the term "checksum" means a CRC-32 (polynomial 0x04C11DB7).

>Note: As in 5.1.13.3 in ISO 26262-11:2018, the probability of a missed detection by a properly working CRC is estimated as  
$P_\text{undetected} ≈ 2^{-32} = 2.33 \cdot 10^{-10}$.

The idea is to use a ASIL-B-grade SW for CRC-verification and to execute it on the R52 (cf. section "Application Notes").
Maybe, we can use QM-grade HW-CRC instead, if the R52 can verify its correctness during runtime (similar to the checkimage for the ISP).

See also **AR-22** in [ExlMap2].

At least the following code/data listed below is considered safety-relevant and is subject to checksum verification:
- the safety-relevant code and data used to implement the safety functions for SG1 to SG4 (e.g., the code to verify the correctness of a received command changing the view configuration)
- the safety monitoring and handling for the safety core (also STL if it is applied as safety measure)
- the data representing the view configuration (in whole or part)


### Build
1. During build time, the build system shall generate checksums on defined code and data sections. The build system shall allocate those checksums in a flash region that can be write-protected.

### Flashing use case
2. During flashing, the flash tool shall store the above into the respective sections and set the write-protection, where required.
3. After flashing, the flash tool shall read back the image, re-calculate the checksums of the relevant code and data sections and compare the checksums to the respective checksums stored in Flash. (In case this cannot be done by the flash tool a different toly may be used for this.)
4. If the compared checksums do not match, the flash tool shall ... (e.g., stop the flashing and raise n checksum error)
(In case this cannot be done by the flash tool a different toly may be used for this.)


### Startup use case
5. At each startup, before the SoC applies safety-relevant code or data from the Flash, the SoC shall load the respective sections into RAM, calculate their checksums and compare them to the respective checksums stored in the Flash. (likely the bootstrap-SW or bootloader-SW are responsible for first checksum verification). (see also Amba documentaion on boot process.)
6. If the compared checksums do not match, the SoC shall ... (e.g., indicate a Safety/CRC error and stop feeding the watchdog).

### Storing use case (after startup)

>Note: Maybe investigate whether frequent use of storage addresses can lead to wear-off. Is wear-levelling supported? Should we add data-mirror areas? If redundant storage is an option, see "Kommentar" below.

7. Befor the SoC is used to store safety-relevant data to the Flash after startup, it shall calculate the data's checksum in a RAM with proper integrity.
8. The SoC shall store that checksum together with the actual data in the Flash so that the checksum can be used to verify the data integrity later.
9. To accomplish the storing procedure, the SoC shall read back that CRC and check its equality with the calculated one.
10. If the compared checksums do not match, the SoC shall ... (e.g., repeat the storing from points 8. and 9. once. If that fails again, the system shall indicate a respective error.)


>Kommentar: Alternativer Ansatz, falls es kein Wear-Levelling gibt, aber die Robustheit bei häufiger Flash-Nutzung eine Rolle spielt:
Checksum der Daten im geschützen RAM berechnen; Speicherung der Daten in zwei unterschiedlichen Flash-Bereichen; Speicherung der Checksum in drittem Bereich.
=> Datenfehler beim Lesen kann erkannt werden, wenn die beiden Datenwerte voneinander abweichen. Die Daten sind mit hoher Wahrscheinlichkeit korrekt, wenn die Checksum reproduzierbar ist.  
>Überschlagsrechnung mit "More than 100,000 Erase/Program Cycles" bei ca. 20 Jahren täglicher Nutzung - und davon 80%:
>$0.8 * 100 000 / (20 * 365.25) \approx 10.95$, entspricht ca. 10 Schreibzugriffen pro Tag.

### Reading use case (after startup)

11. When the SoC is used to read safety-relevant data from the Flash after startup, the SoC shall copy the respective data to RAM, calculate its checksum and compare it to the respective checksum stored in the Flash (cf. Storing use case).
12. If the compared checksums do not match, the SoC shall ... (e.g., retry once and go to safe state if the checksums sitll don't match)

### Power Supply

"The HW design of the SOW2 shall include an appropriate monitoring and handling of the Flash's power."

13. The power supply of each relevant NVM shall be monitored by the PMIC. If the power range for reliable operation (cf. section 9 in [Data Sheet]) is exceeded in any direction, the PMIC shall initiate the transition to the safe state. In this case, the system shall assume the safe state, at latest within ...?  
>**Frage zur Note auf Seite 173:** Ist das mit PMIC umsetzbar?

>Note: VCC Power Supply for IS25WP "1.7V (VMIN) –1.95V (VMAX); 1.8V (Typ)" (page 171 [Data Sheet])

>Note: Latch-Up Min=-100mA Max=+100mA (JEDEC Standard 78)

## SOW2 Safety Manual

- Temperature ranges
  - Storage Temperature: -65°C to +150°C (see "9.1 ABSOLUTE MAXIMUM RATINGS" in [Data Sheet])
  - Operating Range Auto Grade (A3): -40°C to +125°C (see subsection "9.2 OPERATING RANGE" in [Data Sheet])



### optional/QM measures

The following is considered optional/QM, because the checksum detects integrity errors in Flash independently of their cause.
- The Flash is contained in SOW2 with an appropriate casing and insulation for the required opereration environment.
- A proper Write Protection Mode of the Flash is used to protect critical data from accidental overwriting. (cf. subsection "7. PROTECTION MODE" in [Data Sheet]. Note: *"The Password Protection Mode allows an even higher level of security than the Persistent Protection Mode by requiring a 64-bit password for unlocking the device PPB Lock bit."*


## Implementation-related notes

>**NOTE:** According to Amba, the HW-CRC on the SoC has no ASIL grade, and Amba's implementation of SW-CRC neither ([MEKRALANGPOC-245](https://jiraap.ambarella.com/browse/MEKRALANGPOC-245)). Maybe, if we use an STL for the HW-CRC?

>**Comment:** Cryptographic hashes can likely detect more collisions than ordinary hashes like CRC-32. However, the secure hardware extension is part of the Cortex-A53, which is ASIL-QM only. Could it be an option to combine both measures to achieve ASIL-B? Maybe, if we use ARM's Self-Test-Library (STL) for the HW-CRC?


Note the CRC defconfig flags in [iSafetyDefconfig]:
```
CONFIG_CHECK_TARGET_NONE
CONFIG_CHECK_TARGET_BST
CONFIG_CHECK_TARGET_BLD
CONFIG_CHECK_TARGET_ALL
```

>Note application of CONFIG_CHECK_TARGET_BST in  [AmbaBST.asm]. 
>`// BST crc32. Will be replaced by FW programmer`

Note application of CONFIG_CHECK_TARGET_BLD in [AmbaBST_SpiNOR.asm].

Both flags seem to use asm-function `verify_crc32` which seems to use ARM assembler command `crc32x` resp. `crc32w` to calculate 64-bit resp. 32-bit checksum. (There are also assembler commands for 16-bit and 8-bit data)

Some C-code seems to use `IO_UtilityCrc32`.

## Referred documents

[ExlMap2] `(CV22FS) HW Safety Manual SM - SDK Map_updated.xlsx`

[iSafetyDefconfig] `sx/bsp/config/cortex_r/cv2fs_tx32_mvcu01c_isafety_defconfig`

[AmbaBST.asm] `rtos/cortex_a/boot/cv22/secure/bootstrap/AmbaBST.asm`

[AmbaBST_SpiNOR.asm] `rtos/cortex_r/boot/cv2fs/secure/bootstrap/AmbaBST_SpiNOR.asm`

[IPC_man] `SDK8-AN-003_2.2_Ambarella_SDK8_AN_MultiOS_Comm_with_IPC.pdf`

## APPENDIX

>Note: For a general introduction to CRCs, see [A PAINLESS GUIDE TO CRC ERROR DETECTION ALGORITHMS INDEX V3.00 (9/24/96)](https://web.archive.org/web/20181108155847/http://www.repairfaq.org:80/filipg/LINK/F_crc_v3.html)

Guter Link zu CRC-Polynomen und Hamming-Distanzen: <https://users.ece.cmu.edu/~koopman/crc/index.html>

### Q&A

- @Amba: Is the measure SM_SW_CODE_CRC [ExlMap2] also intended for CRC-calculation of general data on demand?

- @Amba: What is the meaning of "because crc32 value checks runtime in each RPC call" in [IPC_man]?




### TODOs from informal Team-Review

- To each verification criterion, think about time constraints (during startup, during streaming, etc.) and specify them.
- Specify in detail HW interface, e.g., for Power Supply safety between PMIC and NVC (in Flash and SoC). Note that the data transfer connections are considered as nominal functions and don't need to be defined here.
- Specify, which code/data is to be verified with the checksum approach.
- Specify, where the checksums for that code/data are to be stored (down to address).
