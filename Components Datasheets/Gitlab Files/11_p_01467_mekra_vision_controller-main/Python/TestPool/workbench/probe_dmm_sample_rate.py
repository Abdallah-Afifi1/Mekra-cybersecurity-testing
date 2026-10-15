# -*- coding: utf-8 -*-
# File : probe_dmm_sample_rate.py
# Task : Find out how fast the DMM can deliver current readings, MVC-92786 needs
#        about 10 ms per sample to resolve a 0.7 s shutter movement
# 1.0.0 | 05.08.2026 |  | initial version
"""
Four ways to read the current are timed against each other. Every one is guarded,
an instrument that does not support a command reports it and the next one runs.
"""
from time import perf_counter

from _automation_wrapper_ import TestEnv

    
SAMPLES = 20                        # readings per timed run
BUFFER_SAMPLES = 200                # readings for the buffered run
TARGET_MS = 10.0                    # what MVC-92786 needs


def timed(label, action, count=SAMPLES):
    """Run action count times and print the average duration."""
    try:
        t_start = perf_counter()
        for _ in range(count):
            action()
        per_sample = (perf_counter() - t_start) / count * 1000.0
        print("%-38s %8.1f ms/sample %s"
              % (label, per_sample, "OK" if per_sample <= TARGET_MS else ""))
        return per_sample
    except Exception as ex:
        print("%-38s failed: %s" % (label, ex))
        return None


def scpi_error(dev):
    """Read the instrument error queue, empty means the commands were accepted."""
    try:
        return dev.query(":SYSTem:ERRor?", delay=0).strip()
    except Exception as ex:
        return "error queue not readable (%s)" % ex


with TestEnv(testcase_id="Probe the DMM sample rate") as testenv:

    dmm = testenv.getDMM()
    dev = dmm._dev                  # raw pyvisa resource, this is a probe

    print("-" * 72)
    print("Target for MVC-92786: %.0f ms per sample or faster" % TARGET_MS)
    print("-" * 72)

    # 1: what the test uses today, MEASure reconfigures on every call
    timed("MEASure via VisaVar current_2A", dmm.current_2A.get)

    # 2: same command without the VisaVar wrapper, isolates the conversion overhead
    timed("MEASure:CURRent:DC? 2A raw",
          lambda: dev.query("MEASure:CURRent:DC? 2A"))

    # 3: configure once, then only trigger and read
    try:
        dev.write("CONFigure:CURRent:DC 2A")
        dev.write("CURRent:DC:NPLC 0.005")
        dev.write("ZERO:AUTO OFF")
        print("Configured once, error queue: %s" % scpi_error(dev))
        timed("READ? after a single CONFigure", lambda: dev.query("READ?"))
    except Exception as ex:
        print("CONFigure block failed: %s" % ex)

    # 4: let the instrument sample into its own memory and fetch the block
    try:
        dev.write("SAMPle:COUNt %d" % BUFFER_SAMPLES)
        dev.write("TRIGger:SOURce IMMediate")
        print("Buffer armed, error queue: %s" % scpi_error(dev))

        t_start = perf_counter()
        dev.write("INITiate")
        block = dev.query("FETCh?")
        elapsed = perf_counter() - t_start

        readings = [v for v in block.strip().split(",") if v]
        print("%-38s %8.1f ms/sample (%d readings in %.3f s)"
              % ("SAMPle:COUNt + INITiate + FETCh?",
                 elapsed / max(1, len(readings)) * 1000.0, len(readings), elapsed))
        print("First three readings: %s" % ", ".join(readings[:3]))
    except Exception as ex:
        print("Buffered sampling failed: %s" % ex)

    print("Error queue at the end: %s" % scpi_error(dev))
    print("-" * 72)

    testenv.breakdown()

print("Done.")
