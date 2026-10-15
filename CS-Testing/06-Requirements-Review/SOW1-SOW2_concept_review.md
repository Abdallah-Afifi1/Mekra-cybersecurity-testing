# Requirement review log: SOW1 - SOW2 interface concept

One entry per requirement, in the order you choose. Every entry uses the same format:

- **SIQ**: questions to raise outside the review (included only when one exists)
- **Impact and proposal**
- **Testability Finding**, **Technical Finding**, **Structure Finding**, **Traceability Finding** (`NONE` when there is nothing)
- **Decision**: left `OPEN` until you decide. I never fill it in.

Sources: `../05-Requirements-Inbox/SecureComm_SOW1-SOW2_and_SecureDebug/` (Polarion export, readyForReview), `../03-Traceability/`, the Volvo Camera Interface Specification D040574 v1.0, SRS rev. 731696.

| # | Requirement | Entry status |
|---|---|---|
| 1 | MVC-119709 | Reviewed, decision OPEN |

---

## 1. MVC-119709 (2.2.1.1.4-4), CAL 2, verified by Test

> The system shall verify the integrity and authenticity of each video frame by comparing the calculated AES-CMAC tag with the 128-bit CMAC tag received in the frame footer.

Downstream: technical requirement MVC-106582, test CS-SOW1-021.

### SIQ

- **SIQ-1 (to the concept owner and Bosch/Volvo).** The Volvo spec (section 11, and the C1-sample settings table) says the AES-CMAC is only available from the 18th frame, "the first 17 frames are without the AES-CMAC Tag". How must SOW2 treat frames 1 to 17: accepted as untrusted video, dropped, or shown? And do the 17 frames count from the start of the stream or from the moment the session key and row information reach the imager?
- **SIQ-2 (to Samsung/Bosch).** The CMAC covers only the rows selected by Start H, Interval H and Total H (Volvo spec: "Header and Image data … by selecting appropriate values"). Which rows does the Mekra concept select, and is a sparse selection (interval of at least 10 rows, MVC-108741) an accepted residual risk?

### Impact and proposal

**Impact.** As written, the requirement says every frame is verified and its integrity is covered. The imager cannot do that: frames 1 to 17 carry no tag, and the tag covers only selected rows. A tester cannot give a pass/fail for frames 1 to 17, and a reader may believe the whole frame is protected.

**Proposal.** Reword to what the design really does, and add the missing behaviour as its own requirement:

1. "The system shall verify the integrity and authenticity of each SOW1 video frame that carries an AES-CMAC tag, by comparing the 128-bit AES-CMAC tag calculated over the selected rows with the 128-bit tag received in the frame footer."
2. New requirement for frames without a tag (frames 1 to 17 after the CMAC is enabled): state whether they are treated as untrusted, dropped, or accepted with a limit on how long this phase may last.
3. Add the applicability: the AES-CMAC is configured for C1-sample onward. The B1/B2-sample settings table in the same Volvo spec lists "Image Authentification by AES-CMAC: None".

**Decision:** OPEN

### Testability Finding

1. **The comparison is not observable by itself.** From outside, only the outcome shows: a frame is accepted or rejected, or an event is logged. That is the same observable as MVC-119710 (reject on failure), so the two tests collapse into one. Proposal: define the observable, for example the security log entry that SRS MVC-108108 already requires on CMAC failure, or a rejected-frame counter, and use it as the pass criterion in both.
2. **"Invalid tag" is not defined.** The concept's verification text lists "incorrect, modified, or invalid". The technical requirement's test adds "partial match is not accepted", which is the better wording. Proposal: use these negative cases: one flipped bit in the tag (first, middle and last byte), a truncated tag, a tag calculated with a different session key, an all-zero tag, and a correct tag on modified authenticated data.
3. **The test needs the session key, which must not be exposed.** To create a "valid frame with a matching tag" the tester must know the SSK. MVC-113706 requires that SOW2 never exposes it. With a real imager the tester cannot know the key, so only the imager's own frames can be checked, and negative cases need an in-line manipulator on the camera link (listed as Missing). With an **imager emulator** that holds the device RSA private key, the tester decrypts the key SOW2 sends (MVC-103055) and can build any frame. Proposal: the emulator is the base setup for this requirement.
4. **Frames 1 to 17** need their own test once SIQ-1 is answered.

**Decision:** OPEN

### Technical Finding

1. **Scope of protection is narrower than the wording.** The tag covers only the selected rows (header with the frame counter if Start H is 0, then every N-th image row). Unselected rows, statistics and other embedded data are not authenticated. The text "integrity and authenticity of each video frame" overstates this. It also contradicts MVC-103033, which says the tag is calculated over the selected rows. Proposal: see the rewording above, and record in the concept which attack the sparse selection is meant to stop (for example stream injection) and which it does not (for example changing unselected rows).
2. **Frames 1 to 17 have no tag** (SIQ-1). The spec text and the requirement disagree.
3. **No time budget.** Holding each frame until verification ends adds latency. Nothing states a limit, and the frame-timing analysis in `Analysis/SG2_Frame_Timing_Requirements_Analysis.docx` should be checked for one. Question for the concept owner: is there a maximum extra latency per frame?

**Decision:** OPEN

### Structure Finding

1. **Two requirements describe one function.** MVC-119709 (verify by comparing) and MVC-119710 (reject if verification fails) are two halves of the same behaviour. The SRS has the same pair (MVC-108117 accept only on match, MVC-108116 reject on mismatch). Proposal: merge into one requirement with an explicit accept and reject outcome, or keep both and make the split clear: 119709 defines the comparison input and result, 119710 defines the reaction.
2. **The technical requirement adds nothing.** MVC-106582 has exactly the same text as MVC-119709. A technical requirement should say how: the algorithm (AES-CMAC with the 256-bit session key, 128-bit tag), the input (the selected rows set by MVC-106576, 108741, 106574, 106583), and what counts as a match (all 128 bits). Proposal: refine the text of MVC-106582 with these.

**Decision:** OPEN

### Traceability Finding

1. **Concept to technical:** MVC-119709 is satisfied by MVC-106582, and MVC-106582 links back (both directions present). One to one.
2. **Upstream link is not specific.** MVC-119709 satisfies MVC-106231, the same item that the debug and hardware-protection requirements link to (for example MVC-103027, MVC-116572). The video-authentication requirements therefore cannot be traced to a particular claim or threat. MVC-106231 is not in the exports, so I could not read what it says. Question: is it the cybersecurity goal for the whole concept, and is there a finer goal (for example "camera stream authenticity")?
3. **SRS:** the likely software realisation is in SRS 23.2.5.2: MVC-108122 (recalculate), MVC-108112 (compare), MVC-108117 (accept only on match). No link exists in the files I have. Proposal: confirm and add the links in Polarion.
4. **The 17-frame rule is traced nowhere.** I searched the concept, the technical requirements and SRS chapter 23.2. No requirement mentions it. It exists only in the Volvo specification.

**Decision:** OPEN
