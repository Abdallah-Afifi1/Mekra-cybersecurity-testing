# -*- coding: utf-8 -*-
# File : MVC-92786-Lens_protection_mechanism_timing.py
# Task : Lens protection mechanism: the shutter exposes the lens within
#        t_shutter_open over the complete ambient temperature range
# 1.0.0 | 14.08.2026 | Ehu Li | initial version

"""
The movement time is derived from the supply current, the motor draws extra
current while the shutter moves.
"""
import threading
from math import isnan
from time import sleep, perf_counter

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92786"

SUPPLY_CH = 1
SUPPLY_V = 24.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_SHUTTER
OPEN = 0x0001
CLOSED = 0x0000
ROI = 0xC0000003                    # human vision, ROI 3, flipped and mirrored

# --- Timing requirement ---
MAX_MOVEMENT_S = 0.7                # t_shutter_open, MVC-91226
SETTLE_S = 1.5                      # image off time of one cycle

# --- Current measurement ---
USE_DMM = True                      # False: poll the supply current of the PSU
DMM_RANGE = "2A"                    # the DUT draws a few hundred mA
DMM_NPLC = 0.005                    # integration time, smaller is faster and noisier
DMM_SAMPLE_S = 0.002                # measured duration of one logged reading
STEADY_S = 0.2                      # tail of the window used as the streaming level
SAMPLE_WINDOW_S = 1.5               # image on time of one cycle, and the log window
BASELINE_S = 0.3                    # leading part of the window used as idle level
MOTION_THRESHOLD_A = 0.02           # current rise that counts as motor running
MIN_MOVEMENT_S = 0.05               # shorter spans are spikes, not a mechanism
MIN_SAMPLES = 20                    # fewer samples make the duration meaningless
DUT_MIN_CURRENT_A = 0.05            # a running DUT draws more than this

# --- Temperature phases ---
# Debug run: LOOPS_PER_PHASE = 2, PHASES = [23.0], ACCLIMATIZE_S = 0.
LOOPS_PER_PHASE = 10                # one run plus nine repetitions
PHASES = [85.0, -40.0, 23.0]        # ambient temperatures in degC

CHAMBER_TOLERANCE = 1.0
CHAMBER_TIMEOUT_S = 120 * 60        # the ramp from 85 degC to -40 degC takes long
CHAMBER_POLL_S = 30

# Nothing is readable while the DUT is off, so the soak is a fixed wait.
ACCLIMATIZE_S = 60 * 60             # shorten when a run has to fit into less time
ACCLIMATIZE_TOLERANCE_K = 8.0       # DUT to chamber difference accepted afterwards


# #############################################################################
# Helper functions
# #############################################################################
def expect_shutter(testresult, client, value, descr):
    """Read the shutter control and expect automatic mode with the given value."""
    return cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, value, descr)


def check_acclimatisation(testresult, client, chamber, phase_t):
    """Compare the DUT temperature with the chamber right after the soak.

    Read directly after power-on, before the DUT has heated itself up again.
    """
    ambient = chamber.getCurrentTemp() if chamber else phase_t
    t_imager, imager_reason = cs.imager_temperature(client)
    t_ser, ser_reason = cs.serializer_temperature(client)

    testresult.addInfo(
        "After the soak at %.0f degC: Tambient %.1f degC, Timager %s, Tser %s"
        % (phase_t, ambient,
           "%.2f degC (%+.1f K)" % (t_imager, t_imager - ambient)
           if t_imager is not None else "not readable (%s)" % imager_reason,
           "%.2f degC (%+.1f K)" % (t_ser, t_ser - ambient)
           if t_ser is not None else "not readable (%s)" % ser_reason))

    value = t_ser if t_ser is not None else t_imager
    if value is None:
        testresult.append(["DUT reached the chamber temperature at %.0f degC: no "
                           "DUT temperature readable" % phase_t, "FAILED"])
        return

    testresult.append(["DUT %.2f degC is %+.1f K from the chamber %.1f degC "
                       "(tolerance %.1f K)"
                       % (value, value - ambient, ambient, ACCLIMATIZE_TOLERANCE_K),
                       "PASSED" if abs(value - ambient) <= ACCLIMATIZE_TOLERANCE_K
                       else "FAILED"])


def current_trace(read, duration_s, out):
    """Poll the current into out as (t in s from start, current in A)."""
    t_start = perf_counter()
    while perf_counter() - t_start < duration_s:
        out.append((perf_counter() - t_start, read()))


def movement_duration(testresult, raw_trace, descr):
    """Derive the movement time from a current trace and write the verdict."""
    # An overload reads NaN, which compares False against every limit.
    trace = [(t, current) for t, current in raw_trace if not isnan(current)]
    if len(trace) < len(raw_trace):
        testresult.addInfo("%d of %d current samples were out of range (NaN) and are "
                           "ignored" % (len(raw_trace) - len(trace), len(raw_trace)))

    if len(trace) < MIN_SAMPLES:
        testresult.append(["%s: only %d current samples in %.1f s, the trace cannot "
                           "resolve %.2f s" % (descr, len(trace), SAMPLE_WINDOW_S,
                                               MAX_MOVEMENT_S), "FAILED"])
        return None

    idle = [current for t, current in trace if t < BASELINE_S]
    if not idle:
        testresult.append(["%s: no sample within the first %.1f s, no idle current to "
                           "compare against" % (descr, BASELINE_S), "FAILED"])
        return None

    baseline = sum(idle) / len(idle)
    limit = baseline + MOTION_THRESHOLD_A

    after = [(t, current) for t, current in trace if t >= BASELINE_S]
    moving = [t for t, current in after if current > limit]
    interval_ms = trace[-1][0] / (len(trace) - 1) * 1000.0

    # The shape goes into the report even when nothing crosses the threshold.
    peak_t, peak = max(after, key=lambda s: s[1]) if after else (0.0, baseline)
    tail = [current for t, current in trace if t >= trace[-1][0] - STEADY_S]
    steady = sum(tail) / len(tail) if tail else peak

    testresult.addInfo("Idle %.4f A, streaming %.4f A, peak %.4f A at %.3f s"
                       % (baseline, steady, peak, peak_t))
    testresult.addInfo("Rise %.4f A over idle, %.4f A over streaming, threshold "
                       "%.4f A, %d samples %.1f ms apart"
                       % (peak - baseline, peak - steady, limit, len(trace),
                          interval_ms))

    if not moving:
        testresult.append(["%s: current never rose above %.3f A, no shutter movement "
                           "detected" % (descr, limit), "FAILED"])
        return None

    # Sampling can only shorten the span, so the verdict takes the upper bound.
    duration = moving[-1] - moving[0]
    worst_case = duration + 2 * interval_ms / 1000.0

    if duration < MIN_MOVEMENT_S:
        testresult.append(["%s: current stayed above the threshold for only %.3f s in "
                           "%d samples, a mechanism cannot move that fast"
                           % (descr, duration, len(moving)), "FAILED"])
        return None

    testresult.append(["%s: shutter moved for %.3f s, at most %.3f s with a %.1f ms "
                       "sample interval (limit %.2f s)"
                       % (descr, duration, worst_case, interval_ms, MAX_MOVEMENT_S),
                       "PASSED" if worst_case <= MAX_MOVEMENT_S else "FAILED"])
    return worst_case


def subscribe_while_logging(testresult, client, psu, dmm):
    """Send the subscribe while the current is recorded, return (rx, trace).

    The DMM records into its own memory, the PSU has to be polled in a thread.
    """
    packet = cs.build_request(cs.M_SUBSCRIBE_ROI_VIDEO, 0x0C, ROI.to_bytes(4, "big"))

    if USE_DMM:
        dmm.startCurrentLog(int(SAMPLE_WINDOW_S / DMM_SAMPLE_S))
        t_start = perf_counter()
        sleep(BASELINE_S)

        # Sent without waiting, a missing response would stretch the window.
        client.send_packet_dont_wait_for_response(packet, client.serverIP,
                                                  int(client.destinationPort))
        values = dmm.fetchCurrentLog()
        interval = (perf_counter() - t_start) / max(1, len(values))

        return client.receive_packet(), [(i * interval, v)
                                         for i, v in enumerate(values)]

    trace = []
    read = getattr(psu, "current_ch%d" % SUPPLY_CH).get
    sampler = threading.Thread(target=current_trace,
                              args=(read, SAMPLE_WINDOW_S, trace))
    sampler.start()

    sleep(BASELINE_S)                   # collect the idle level first
    rx = cs.send_wait(client, packet)
    sampler.join()
    return rx, trace


def open_shutter_and_measure(testresult, client, psu, dmm, descr):
    """Subscribe the ROI while recording the current, return the movement time."""
    rx, trace = subscribe_while_logging(testresult, client, psu, dmm)

    # A DUT that did not take the subscribe never moved its shutter.
    if not cs.positive_response(testresult, rx, cs.M_SUBSCRIBE_ROI_VIDEO,
                                "subscribeROIVideo (0x%08X, ROI %d)"
                                % (ROI, ROI & 0xFF)):
        testresult.addInfo("%s: current trace not evaluated" % descr)
        return None

    return movement_duration(testresult, trace, descr)


def shutter_cycle(testresult, client, psu, dmm, phase_t, loop):
    """One measurement: closed -> open with current logging -> closed again."""
    descr = "%.0f degC loop %d/%d" % (phase_t, loop, LOOPS_PER_PHASE)
    testresult.addSubHeader("Shutter movement at %s" % descr)

    expect_shutter(testresult, client, CLOSED, "closed before the stream starts")
    duration = open_shutter_and_measure(testresult, client, psu, dmm, descr)
    expect_shutter(testresult, client, OPEN, "open while the stream is active")

    cs.unsubscribe_roi(testresult, client, ROI)
    sleep(SETTLE_S)
    return duration


# #############################################################################
# Test
# #############################################################################
with TestEnv(testcase_id=TESTCASE_ID) as testenv:

    testresult = testenv.getResults()
    psu = testenv.getPSU()
    client = None

    try:
        chamber = testenv.getCC()
    except Exception as ex:
        chamber = None
        testresult.addInfo("Climate chamber not available: %s" % ex)

    dmm = testenv.getDMM() if USE_DMM else None
    if USE_DMM:
        dmm.configureCurrentDC(DMM_RANGE, DMM_NPLC)

    try:
        # #####################################################################
        testresult.addHeader("Preconditions")
        # #####################################################################
        cs.log_dut_config(testresult)
        testresult.addInfo("Current recorded with the %s"
                           % ("DMM log, %s range, NPLC %s, %d readings per cycle"
                              % (DMM_RANGE, DMM_NPLC,
                                 int(SAMPLE_WINDOW_S / DMM_SAMPLE_S))
                              if USE_DMM else "PSU on channel %d" % SUPPLY_CH))

        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        # A blown DMM input fuse shows as no current while the PSU still delivers.
        psu_current = getattr(psu, "current_ch%d" % SUPPLY_CH).get()
        dmm_current = dmm.readCurrentDC() if USE_DMM else float("nan")
        testresult.append(["DUT draws current after startup: PSU %.4f A, DMM %.4f A"
                           % (psu_current, dmm_current),
                           "PASSED" if psu_current > DUT_MIN_CURRENT_A else "FAILED"])

        # #####################################################################
        for phase_t in PHASES:
            testresult.addHeader("Tambient = %.0f degC, %d movements"
                                 % (phase_t, LOOPS_PER_PHASE))
        # #####################################################################
            cs.chamber_temperature(testresult, chamber, phase_t, CHAMBER_TOLERANCE,
                                   CHAMBER_TIMEOUT_S, CHAMBER_POLL_S)

            # The DUT only reaches the chamber temperature while it is off.
            client.close_socket()
            client = None
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

            testresult.addInfo("Soaking %.0f min with the DUT powered off"
                               % (ACCLIMATIZE_S / 60.0))
            sleep(ACCLIMATIZE_S)

            client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)
            check_acclimatisation(testresult, client, chamber, phase_t)

            durations = []
            for loop in range(1, LOOPS_PER_PHASE + 1):
                duration = shutter_cycle(testresult, client, psu, dmm, phase_t, loop)
                if duration is not None:
                    durations.append(duration)

            # Every cycle has to be measured, an unmeasured one fails the phase.
            if durations:
                testresult.append([
                    "%d of %d cycles measured at %.0f degC, slowest at most %.3f s "
                    "(limit %.2f s)"
                    % (len(durations), LOOPS_PER_PHASE, phase_t, max(durations),
                       MAX_MOVEMENT_S),
                    "PASSED" if (len(durations) == LOOPS_PER_PHASE
                                 and max(durations) <= MAX_MOVEMENT_S) else "FAILED"])
            else:
                testresult.append(["No cycle could be measured at %.0f degC"
                                   % phase_t, "FAILED"])

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        if client is not None:
            client.close_socket()

        cs.release_chamber(chamber)

        if POWER_OFF_AT_END:
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

        sleep(0.5)

print("Done.")
