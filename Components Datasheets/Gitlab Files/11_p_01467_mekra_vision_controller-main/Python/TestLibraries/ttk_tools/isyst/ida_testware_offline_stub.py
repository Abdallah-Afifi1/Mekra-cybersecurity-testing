#******************************************************************************
# -*- coding: utf-8 -*-
# File   : ida_testware_offline_stub.py
# Package: ttk_tools.isyst
# Task   : High-level access to stubbed/mocked iDA Testware interfaces
#
# Type   : Implementation
# Python : 3.6+
#
# Copyright 2024 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 15.03.2024 | J.Tremmel  | initial, adapted from ida_testware 1.2.0 
# 1.0.1  | 28.03.2024 | J.Tremmel  | docstring tweaks, fixed log level handling 
#                                  | in recorder messages
#******************************************************************************
"""
@package ttk_tools.isyst.ida_testware
Access to stubbed/mocked iDA Testware interfaces.

iDA Testware offline stubs use the connection address as context for connecting
to the default offline data provider (for offline implementations of MwAppRpc/MwRecRpc).

Example: Provide initial data
    addr = "127.0.0.1"
    
    dp = offline_data_provider.getDefaultProvider()
    
    # initialize default data (uninitialized entries will default to float 0.0)
    dp.setData(addr, "foo", 113)
    dp.setData(addr, "bar", 456)
    dp.setData(addr, "baz", 789)
    dp.setData(addr, "qux", 11.11)
    dp.setData(addr, "etaoin[0]", 1)
    dp.setData(addr, "etaoin[1]", 2)
    dp.setData(addr, "etaoin[2]", 3)
    
    dp.setData(addr, 'Analog_In.KL30_Rueckmessung', 13.98) # CV_monitor
    dp.setData(addr, 'Analog_In.CCmon',              0.48) # CC_monitor
    dp.setData(addr, 'Analog_Out.MotorTemp',        20.00) # motor_temp
    
    with IdaRecorder(addr) as recorder: # using the default port
        recorder.setup(["Triangle.uint32", "Sine.float64", "Counter"])
        # recorder.setup will raise an MwRecError if setup failed
        
        recorder.start()
        time.sleep(3.0)
        recorder.stop()
        
        daq_data = recorder.getData()
        idaq.printDataInfo(daq_data, outer_n=8)
            
    with IdaTestware(addr) as ida: # using the default port
        mwvar = ida.getMwVar("foo")
        print(mwvar.getValue())
    
    Instead of with-context handlers, the iDA interfaces are often configured
    as part of a TestEnv instance and accessible via getters, e.g.
    testenv.getHilRecorder().
    
Example: Variable abstraction and Var containers
    # In test scripts, Variables will usually be accessed via a (hil) var container:

    # hil_variables.py
    from ttk_base.isyst_ida.variables import Var as HilVar
    from ttk_base.isyst_ida.variables import VarContainer as HilVarContainer
    
    class HilVars(HilVarContainer): 
        def __init__(self, ida):
            super().__init__(ida)
            self.CV_vorgabe = HilVar(ida, 'Analog_Out.CVprog', unit="V", fmt="flt2", resettable=False)
            self.CC_vorgabe = HilVar(ida, 'Analog_Out.CCprog', unit="A", fmt="flt3")
            self.CV_monitor = HilVar(ida, 'Analog_In.KL30_Rueckmessung', unit="V", fmt="flt2")
            self.CC_monitor = HilVar(ida, 'Analog_In.CCmon',             unit="A", fmt="flt3")
            self.KL30       = HilVar(ida, 'Digital_Out.KL30', lookup={0: "off", 1: "on"}, fmt="int", resettable=False)
            self.KL15       = HilVar(ida, 'Digital_Out.KL15', lookup={0: "off", 1: "on"}, fmt="int", resettable=False)
            self.motor_temp = HilVar(ida, 'Analog_Out.MotorTemp', unit="°C", descr="Motor temperature")

    # Usually, an instance of the container can later (in a test script) be accessed via 
    hil = testenv.getHil()
    print(hil.CC_monitor.get()) 
    print(hil.CC_monitor.info()) 
"""
import time

from ttk_tools.isyst.mwapp_client_offline_stub import MwAppRpc # @UnresolvedImport (compiled extension)
from ttk_tools.isyst.mwrec_client_offline_stub import MwRecRpc # @UnresolvedImport (compiled extension)

from ttk_tools.isyst import idaq                  # @UnresolvedImport (compiled extension)
from ttk_tools.isyst.ida_common import MwAppError # @UnusedImport
from ttk_tools.isyst.ida_common import MwRecError, RecState, RecCommandStatus


# #############################################################################
class IdaTestware:
    """ Access to iDA Testware MwApp interface for reading/writing variables """
    
    ## gRPC connection options.
    # If set, define as a list of (name, value) tuples, e.g.
    # [('grpc.max_receive_message_length', 1024 * 1024 * 8), ]
    channel_options = None
    
    # #########################################################################
    def __init__(self, addr="127.0.0.1", port=50051):
        """ Parameters:
                addr     - connection target address string (IP),
                           e.g. "192.168.2.123".
                port     - connection target port, defaults to 50051 for MwApp
        """
        self.mwapp = MwAppRpc(
            target=f"{addr.strip()}:{port}",
            channel_options=self.channel_options
        )

    @property
    def system_name(self):
        """ Name from active system configuration. """
        return self.mwapp.system_name

    @property
    def service_version(self):
        """ Version of running iDA Testware service. """
        return self.mwapp.system_version
        
    @property
    def instance_key(self):
        """ Key of the active iDA Testware service, changes each time the 
            service is (re-) started.
        """
        return self.mwapp.instance_key
    
    
    # #########################################################################
    def getMwVar(self, var_name):
        """ Factory method for creating an iDA Testware MwVar proxy instances.
            Mainly intended for convenience, so the variable abstraction 
            (see ttk_base.isyst_ida) does not have to import additional packages.
            
            Parameters:
                var_name  -  variable name on iDA Testware mwservice
            
            Info: MwVar Proxy Instances:
                MwVar instances proxy access for a specific variable to the 
                main MwApp interface.
                
                Properties:
                    * mwvar.name      - name of variable
                    * mwvar.var_id    - internal Var-ID on service
                    * mwvar.data_type - data type of variable
                    * mwvar.size      - size; 1: scalar, > 1: array variable 
                    * mwvar.unit      - value unit string
                    * mwvar.fmt       - value format hint string
                    
                Methods:
                    * mwvar.getValue() => value
                    * mwvar.setValue(value)
                    * mwvar.updateValue(value) => prev_value
                    * mwvar.resetValue()
                
            Returns an initialized MwVar instance
        """
        # not much to it:
        return self.mwapp.getMwVar(var_name)


    # #########################################################################
    def resetVars(self, var_ids=None, reset_all=False, complete_arrays=False):
        """ Reset one or more variables to their original values.
            This will directly reset variables in the data model to their 
            default values from system configuration.
            
            Parameters:
                var_ids         - list of Var-IDs to reset
                
                reset_all       - True:  reset all variables, var_ids will be ignored
                                  False: reset only those variables listed in var_ids
                                  
                complete_arrays - True:  reset all array elements if head element 
                                         (index [0]) is in var_ids  
                                  False: only array elements in var_ids will be 
                                         reset (does not matter with reset_all=True)
        """
        self.mwapp.resetValue(
            var_ids=var_ids, 
            reset_all=reset_all, 
            complete_arrays=complete_arrays
        )


    # #########################################################################
    def getGroups(self):
        """ Get configured variable groups (and Var-IDs in those groups).
            For array-Variables, only the head element's Var-ID will be included.
            
            Returns a dict with <group_id>: {
                "group_name": "<group_name>",
                "group_id":   <group_id>,
                "var_ids":    [<var_id1>, <var_id2>, ... <var_idn>],
                "var_names":  [<var_name1>, <var_name2>, ... <var_namen>], 
            }
        """
        return self.mwapp.getGroups()
        
    # #########################################################################
    def getVarNames(self):
        """ Get a all configured variable names.
            Meta data has been retrieved during init, so this will just return
            all cached names. 
            Note: 
                Each element of array variables will be included separately
            
            Returns an iterator of variable names.
        """
        vmc = self.mwapp.var_meta_cache
        return (vmc.getDisplayName(var_id) for var_id in vmc.keys())
        
        
    # #########################################################################
    def close(self):
        """ Close current connection """
        self.mwapp.close()
        
    # #########################################################################
    # Context Manager - for convenience 
    # #########################################################################
    def __enter__(self):
        """ Start connection as managed context """
        return self
    
    # #########################################################################
    def __exit__(self, exc_type, exc_value, tb):  # @UnusedVariable
        """ End context manager. """
        self.close() # close opened connection
        return False
    

# #############################################################################
class IdaRecorder:
    """ Data acquisition using an iDA Recorder application. 
        
        Example:
            rec = IdaRecorder(addr="127.0.0.1") 
            # usually gets set up somewhere in TestEnv
            # e.g. rec = testenv.getHilRecorder()
            
            rec.setup([
                "scheduler.Primary.runtime", 
                "tasklevel.Recorder_runtime", 
                "some.other.variable",
                hil.motor_temp         # or directly use HIL Var instances
            ])
            
            rec.start()
            time.sleep(5.0) # or do something else while recording runs
            rec.stop()
            
            daq_data = rec.getData()
            
            # usually gets closed in testenv.breakdown()
            rec.close() 
    """
    
    ## gRPC connection options.
    # If set, define entries as a list of (name, value) tuples, e.g.
    # [('grpc.max_receive_message_length', 1024 * 1024 * 8), ]
    channel_options = None
    
    ## level of log verbosity:
    # 0: mostly silent
    # 1: status messages
    # 2: more elaborate status messages
    verbosity = 1
    
    # #########################################################################
    def __init__(self, addr="127.0.0.1", port=50055):
        """ Parameters:
                addr     - connection target address string (IP),
                           e.g. "192.168.2.123".
                port     - connection target port, defaults to 50055 for MwRec
        """
        self.mwrec = MwRecRpc(
            target=f"{addr}:{port}", 
            channel_options=self.channel_options
        )
    
    def _log(self, level, *args, **kwargs):
        if self.verbosity >= level:
            print(*args, **kwargs)

    # #########################################################################
    def setup(self, variables):
        """ Setup recorder for data acquisition (configure what variables to measure).
            Basic variant for symmetry with other implementations 
            
            Note:
                setup() may only be performed while data acquisition 
                is not already running.
            
            Parameters:
                variables - list/iterable of gamma variables to measure
            
            Usage:
                # direct setup with variable names
                daq.setup([
                    "some_var.foo", 
                    "some_other_var"
                ])
                # or, when using a VarContainer:
                daq.setup([hil.some_var, hil.some_other_var])
                
        """
        # setupVars will raise an MwRecError if setup failed
        return self.mwrec.setupVars(var_names=variables)
    
    
    # #########################################################################
    def start(self):
        """ Start recorder data acquisition with configured variables.
            Returns a RecCommandStatus (usually success).
        """
         
        self._log(1, "# data acquisition: start...")
        state = self.mwrec.getState()
        if state in (RecState.start_recording, RecState.recording):
            self._log(1, "[stopping] currently active recording")
            self.stop() # just for (potential) recovery
            time.sleep(0.100)
        
        status = self.mwrec.startRecording()
        if status != RecCommandStatus.success:
            raise MwRecError(f"Failed to start recorder", status)
        return status
    
    # #########################################################################
    def stop(self):
        """ Stop a currently running data acquisition. 
            Returns a RecCommandStatus (usually success).
        """
        self._log(1, "# data acquisition: stop...")
        return self.mwrec.stopRecording()
    
    
    # #########################################################################
    def getData(self):
        """ Get recorded data and return it as a daq data structure.
            
            Returns a daq data structure with {  
                <label>: {  
                    "time": [<time_s>, <time_s>, ...],  
                    "data": [<value>,  <value>,  ...],  
                    "type": "<datatype-string>"  
                },  
            } entries.
        """
        state = self.mwrec.getState()
        if state != RecState.stopped:
            # if getData is called while recorder is not yet configured or 
            # currently running, only an empty data set would be returned
            # (as no data is available).
            # Better to provide a more obvious error message:
            raise MwRecError(
                f"Cannot get recorded data, invalid state "
                f"(expected {RecState.stopped!r}, got {state!r})"
            )
            
        idaq_data = self.mwrec.getIdaqDataIO()
        daq_data = idaq.readDaqData(idaq_data)
        if self.verbosity >= 2:
            print(f"--> data contains measurements for {len(daq_data)} signals:")
            for label, data in daq_data.items():
                print(f"    ({data['type']}) {label:<42}  # {len(data['time'])} records")
            
        return daq_data
    
    # #########################################################################
    def close(self):
        """ Close current connection """
        self.mwrec.close()
        
    
    # #########################################################################
    # Context Manager - for convenience 
    # #########################################################################
    def __enter__(self):
        """ Start daq/recorder as a managed context 
            
            Example:
                with IdaRecorder(addr="127.0.0.1") as daq:
                    daq.setup([
                        "tasklevel.Recorder_runtime", 
                        "Analog_In.CVmon",
                        "Analog_In.CCmon",
                    ])
                    daq.start()
                    time.sleep(2.0) # or do something else while recording runs
                    daq.stop()
                    daq_data = daq.getData()
        """
        return self
    
    # #########################################################################
    def __exit__(self, exc_type, exc_value, tb):  # @UnusedVariable
        """ End context manager.
            Note:
                Exiting the context manager will not stop a currently
                running recording.
        """
        self.close() # close opened channel
        return False


# #############################################################################
# @cond DOXYGEN_IGNORE 
# #############################################################################
if __name__ == '__main__':  # pragma: no cover (contains only sample code)
    from matplotlib import pyplot as plt
    
    # connection target
    target_addr = '192.168.56.8' # VM
    
    def showPlotAIO(daq_data):
        """ PLot all signals into a single plot (all-in-one) """
        _fig, ax = plt.subplots(
            1, 1,
            figsize=(16, 6), facecolor="#EEEEEE",
            num="Data Acquisition", layout='tight',
        )
        ax.set_title("Recorded Data") 
        ax.set_xlabel("time [s]")
        ax.set_ylabel("values")
        
        for label, var_data in daq_data.items():
            ax.plot(var_data["time"], var_data["data"], label=label)
        ax.grid(True)
        ax.legend()
        
        plt.show()
        plt.close() 
    
    
    def showPlot(daq_data):
        """ PLot signals into separate plots with linked time axis,
            but place all "runtime" signals in a shared plot. 
        """
        runtime_labels = [s for s in daq_data if "runtime" in s]
        # 1 plot for runtime signals,
        # 1 plot for each non-runtime signal
        num_plots = 1 + len(daq_data) - len(runtime_labels) 
        
        _fig, axs = plt.subplots(
            num_plots, 1, sharex=True, # shared axes will be linked in view
            figsize=(16, 6), facecolor="#EEEEEE",
            num="Data Acquisition", layout='tight',
        )
        
        signal_plot_idx = 0
        for idx, (label, var_data) in enumerate(daq_data.items()):
            if label in runtime_labels:
                # group all runtime signals in first plot
                ax = axs[0] 
                ax.set_ylabel("runtime [µs]")
            else:
                # place all other signals their own plots
                signal_plot_idx += 1
                ax = axs[min(signal_plot_idx, num_plots - 1)] 
                ax.set_ylabel("value")
                
            # assign line colors manually, so signals get different colors across plots
            # (otherwise all signals start with same first color in each plot)
            # color C<i> => index in color cycler (plt.rcParams['axes.prop_cycle'])
            ax.plot(var_data["time"], var_data["data"], label=label, color=f"C{idx}")
            
        for ax in axs:
            ax.grid(True)
            ax.legend(loc="upper right") # fixed position has better performance
            
        # tick labels of inner axes are automatically removed by sharex (and sharey)
        axs[-1].set_xlabel("time [s]")
        
        plt.show()
        plt.close()
    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    with IdaTestware(addr=target_addr) as tw:

        print(f"System Name:          {tw.system_name}")
        print(f"Service version:      {tw.service_version}")
        print(f"Service instance key: {tw.instance_key:X}")
        
        # Group names + variables in group
        # Note: groups will only show the head element of array variables
        
        # print("-" * 120)
        # for group_data in tw.getGroups().values():
        #     print(f"# {group_data['group_name']}")
        #     for var_name in group_data['var_names']:
        #         print(f"    {var_name}")
        
        print("-" * 120)
        print("# Groups:")
        for group_data in tw.getGroups().values():
            print(f"  {group_data['group_name']:<42} ({len(group_data['var_names'])} variables)")
        
        print("-" * 120)
        print("# All defined variables:")
        for var_name in tw.getVarNames():
            # print(var_name)
            var = tw.getMwVar(var_name)
            print(f"  {var_name:<42} ► {var.getValue()!r} {var.unit}")
            
        tw.resetVars(reset_all=True)
        
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    with IdaRecorder(addr=target_addr) as daq:
        print("-" * 120)
        print("# recorder setup")
        daq.setup([
            "scheduler.Primary.runtime", 
            "scheduler.Primary.runtime.cycle",
            "tasklevel.Recorder_runtime", 
            "tasklevel.MainSyncPrimary_runtime",
            
            "TriangleSignal",
            "Sine.float64",
        ])
        daq.start()
            
        duration_s   = 3
        step_delta_s = 0.200
        
        print(f"Recording for {duration_s:.1f}s...")
        steps = int(round(duration_s / step_delta_s))
        for i in range(1, steps + 1):
            try:
                state = daq.mwrec.getState()
                if state not in (RecState.start_recording, RecState.recording):
                    print("\n--> aborted")
                    break
                print("|", end=(f" ({i}/{steps})\n" if i % 100 == 0 else ""))
                    
                time.sleep(step_delta_s)
            except KeyboardInterrupt:
                print("\n--- manual abort ---")
           
        print()
        daq.stop()
        time.sleep(.100)
        daq_data = daq.getData()
        for label, entries in daq_data.items():
            if entries["data"]:
                min_val = min(entries["data"])
                max_val = max(entries["data"])
                average = sum(entries["data"]) / len(entries["data"])
                print(f"{label:<42}: "
                      f"min {min_val:7.2f} µs, max {max_val:7.2f} µs, "
                      f"average {average:7.2f} µs")
                
        print("# Data:")
        idaq.printDataInfo(daq_data, outer_n=8)
        
        
        showPlot(daq_data)
        #showPlotAIO(daq_data)
        
    print("Done.")
# @endcond DOXYGEN_IGNORE
# #############################################################################
