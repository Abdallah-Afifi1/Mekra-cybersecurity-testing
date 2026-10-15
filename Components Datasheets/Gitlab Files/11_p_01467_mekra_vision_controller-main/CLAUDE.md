# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

HIL test automation for the MEKRA Vision Controller (Volvo SOW 2, rear/trailer camera; see `README.md`). Test scripts drive real lab hardware — power supplies, multimeter, climate chamber, Ethernet switch — against a camera DUT over Ethernet (DHCP → SOME/IP → RTP video).

This is **not** a normal Python package: there is no pytest, no linter config, no build step. Scripts are executed top-to-bottom by the **iSyst iTestStudio** runner using the **TestToolkit (`ttk_*`)** libraries. `hil_project.ini` tells iTestStudio which folder plays which role.

### The iTestStudio dependency — and what still works without it

`_automation_wrapper_.py:26-44` resolves `libraries/test_support<major><minor>.pyz` under the `ITESTSTUDIO_PATH` environment variable and inserts it into `sys.path`; that pyz provides `test_environment` (`TestEnvironmentBase`) and `result_list` (the `ResultList` / `SubResult` base classes that `TestLibraries/test_result_list.py` extends). Without iTestStudio installed, **anything going through the wrapper** — i.e. every test script — dies at `from test_environment import TestEnvironmentBase` (`_automation_wrapper_.py:46`).

The `ttk_*` packages, by contrast, are **vendored into `Python/TestLibraries`, partly as compiled `.pyd` binaries** (e.g. `ttk_base/_variables_base.pyd`, `_values_base.pyd`, `configuration.pyd`). So the device-driver layer *is* importable on a plain machine:

```bash
cd Python/TestLibraries
python -c "import sys; sys.path.insert(0,'.'); \
  from tools.toellner.psu_toe8941 import TOE8941; print(TOE8941)"
```

Use this to check a driver's real API instead of guessing. Instantiating a class still opens a VISA session, so it needs hardware — but imports, signatures and `inspect` work offline. Everything else offline is static: `py_compile`, `git diff`, AST inspection.

Both the `.pyz` and the `.pyd` files are **CPython-version-specific** (hence the `%d%d` in the pyz name) — the interpreter running the tests must match what is installed/vendored. This machine has Python 3.12.10 and the vendored `.pyd`s load under it.

## Commands

```bash
# dependencies (pywin32, matplotlib, pyvisa, msgpack, requests)
pip install -r requirements.txt

# run one test script outside iTestStudio (needs ITESTSTUDIO_PATH + hardware).
# sys.path[0] becomes TestPool/, which is what makes `_automation_wrapper_` importable.
python "Python/TestPool/MVC-12345-B-Sample_functional_B.py"

# syntax check without hardware — safe, executes nothing
python -m py_compile "Python/TestPool/<script>.py"

# inspect a driver's real API without hardware (see next section)
cd Python/TestLibraries && python -c "import sys; sys.path.insert(0,'.'); \
  import inspect, tools.toellner.psu_toe8941 as m; print(inspect.getsource(m.TOE8941.outputEnable))"

# clear all __pycache__ folders
"### clean __pycache__ ###.bat"
```

Normal operation is through the iTestStudio GUI: pick a `.ser` series, or run a single script from the test pool. Results land in `TestReports/` (`SingleTest.xml` / `SingleTestManual.xml` per `hil_project.ini [RESULTS]`).

Some scripts use double quotes nested inside f-strings and therefore need **Python 3.12+**.

## Architecture

### Three folders, wired by `hil_project.ini`

| Folder | Role |
|---|---|
| `Python/TestPool` | test scripts — the actual tests; subfolders `electrical_tests/`, `development_support/`, `examples/`, `workbench/` |
| `Python/TestLibraries` | device drivers (`tools/`), the vendored TestToolkit (`ttk_base`, `ttk_tools`, `ttk_checks`, …) and `test_result_list.py` |
| `TestStructure` | XML test structure: `*.seq` (sequence = list of scripts) referenced by `*.ser` (series) |

### `Python/TestPool/_automation_wrapper_.py` is the hub

Every test script begins with `from _automation_wrapper_ import TestEnv`. The wrapper bootstraps `sys.path`, then `TestEnv` (a `TestEnvironmentBase` subclass, usable as a context manager) provides **lazy, cached device factories**:

| Factory | Device | Address |
|---|---|---|
| `getPSU()` | R&S NGP800 (4 channels) | `TCPIP0::192.168.10.10` |
| `getPSU_TOE()` | TOELLNER TOE 8941 (single output) | `ASRL5::INSTR` (USB → virtual COM port) |
| `getDMM()` | Siglent SDM3065X | `TCPIP0::192.168.10.20` |
| `getCC()` | Vötsch VT7004 climate chamber | `192.168.10.40` |
| `getEES()` | Technica TE200x Ethernet switch | `10.104.3.30` |

Adding a device means touching **three** places consistently: an `self.<x> = None` slot in `__init__`, a `close()` block in `breakdown()`, and the factory itself. `breakdown()` (called by `__exit__`) closes every instantiated device and stores the results — a device that is not closed there leaks its VISA session and stays in remote mode.

### Canonical test script shape

```python
#*****...  header block: File / Task / Copyright / version table
#          → parsed by the runner into the report meta-data, keep it in sync
from _automation_wrapper_ import TestEnv

def cleanup():          # module-global helper, usually a bare try/except
    ...                 # switch outputs off, unsubscribe streams

try:
    with TestEnv(testcase_id="MVC-12345-B-Sample_functional_B") as testenv:
        testresult = testenv.getResults()
        psu = testenv.getPSU()
        ...
        testresult.addCheckAbsTol(psu.voltage_ch1, 28, abs_tol=0.02,
                                  descr="Check PSU output voltage")
finally:
    cleanup()
    testenv.breakdown()
print("Done.")
```

`testcase_id` must be unique per script (conventionally the filename stem): it becomes `<testcase_id>` in the report and determines the result file name, so two scripts sharing an ID overwrite each other's results.

Result API lives in `Python/TestLibraries/test_result_list.py` — `addCheckAbsTol`, `addCheckRelTol`, `addCheckRange`, `addCompareCE`, `addBoolean`, `addSubHeader`, `addInfo`, and the raw `append(["text", "PASSED"|"FAILED"|"INFO"|"ERROR"])`. An image is embedded by putting `f"[[IMG]] {path}"` into a result row.

### VISA driver pattern (`tools/visa_variable.py`)

Instrument values are `VisaVar` objects built from a `get_cmd` / `set_cmd` pair, with `.get()`, `.set(v)` and `.info()`. They are **passed by reference** into the check functions, which query the device at check time — hence `addCheckAbsTol(psu.voltage_ch1, …)` and *not* `psu.voltage_ch1.get()`. `checkedQuery()` / `checkCommandErrors()` drain `SYSTem:ERRor?` after commands and raise `ScpiCommandError`.

Each driver class opens its VISA resource **in `__init__`** (printing a banner, re-raising on failure) and must be `close()`d — `close()` returns the device to local/manual mode but deliberately leaves the shared `ResourceManager` open.

Driver APIs are **not** interchangeable across models. Example: NGP800 is 4-channel with a two-stage output (`channelOutputEnable(ch, x)` **and** `masterOutputEnable(x)`) and `_ch1..._ch4` suffixed variables; TOE 8941 is single-output with `outputEnable(x)` and unsuffixed `voltage_preset` / `voltage` / `current`. Beware same-looking names with different meaning — NGP800's `*_min/_avg/_max` are measurement statistics, TOE 8941's `*_min/_max` are the model's settable range.

### DUT / camera domain layer (`Python/TestLibraries/tools/`)

Bench network is `192.168.120.x`, the camera is `.10`. A typical functional test runs: `DHCPServer` hands the camera an address → `ServiceDiscovery` on multicast `239.120.1.1:30490` yields the configuration → `someip_commands` (`getCamIdentification`, `subscribeROIVideo`, …) exchange SOME/IP payloads → `rtpSniffer` confirms frames and `GStreamer` grabs `.jpg` stills (HVS port 5015, MVS port 5048) into `TestReports/Initial_Test/TestData`. Expected values come from `TestLibraries/reference_value/` and from an Excel sheet under `TestPool/Data_import/`.

### Registering a test so it actually runs

A `.py` file in the test pool is invisible to a series until a sequence references it **by filename**:

```xml
<!-- TestStructure/TestSequences/<name>.seq -->
<singletest source="MVC-12345-B-Sample_functional_B.py" />   <!-- path relative to TestPool -->
```

and that `.seq` is listed in a `.ser` (`<testsequence source="…seq" />`). Currently 60 of the 61 sequences reference `MVC-12345-B-Sample_functional_B.py`; the exception is `FF_chip_test.seq`.

## Conventions

- Test scripts are named `MVC-<id>-<Description_with_underscores>.py`.
- Every file opens with the `#***` banner including the version table; add a row (`Ver. | Date | Name | Description`) when you change a file rather than editing history.
- Code, comments and report strings are English even though the team communicates in German.
- New instrument drivers go to `tools/<vendor>/<type>_<model>.py` with a vendor-level `__init__.py`, following the `VisaVar` pattern above.

## Repo gotchas

- `venv/` and `sow2/` (~1500 files each) are committed despite `.gitignore`; `venv/` even points at a different user's home directory. Don't use them and don't unilaterally clean them up.
- **30 `.pyc` files under `Python/` are tracked** despite `.gitignore` (plus more inside `venv/`/`sow2/`). Consequence: merely *importing* a module rewrites tracked files and they show up as ` M` in `git status`. After any local import experiment, check `git status` and `git checkout -- <the .pyc>` — do not commit them. Some, like `TestPool/__pycache__/_automation_wrapper_.cpython-313.pyc`, are already stale (inert, since Python revalidates by mtime/size).
- `TestPool/electrical_tests/MVC-92704-Momentary_drop_in_supply_voltage` has no `.py` extension and can never run.
- `test_result_examples/` exists twice — under `TestPool/` and under `TestPool/examples/`.
- Vendor manuals for every instrument (NGP800, SDM3065X, VT7004, TE-200x) plus the iTestStudio workshop slides are in `Documentation/` — consult them before guessing at SCPI commands.
