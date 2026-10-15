#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : plot_utils.py
# Task    : Utility function samples for plotting data
# Python  : 3
#
# Copyright 2016 - 2023 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 24.05.2016 | J.Tremmel | initial
# 1.1.0  | 31.05.2016 | J.Tremmel | added parameters fig_size and fig_dpi to plotSignals
# 1.2.0  | 08.11.2018 | J.Tremmel | switched from ancient pylab to pyplot
# 1.2.1  | 22.05.2023 | J.Tremmel | added tight_layout param to figure 
#******************************************************************************
from matplotlib import pyplot 


# #############################################################################
def plotSignals(daq_data, variables=None, out_file_path=None, 
                xlabel="time", ylabel="values", title="data", 
                fig_size=(14, 4), fig_dpi=72):
    """ Simple plotting of signals using matplotlib.
        This example is intended as a starting point for custom plotting functions.
        Adapt as needed for the specific use case.
        
        See http://matplotlib.org/ for available options and usage.
        
        Parameters:
            daq_data      - data acquisition data structure containing data for 
                            variables. See ttk_daq.daq_utils for a data structure
                            description.
            variables     - list/iterable of variables to add to plot.
                            If Var instances are provided, the plot legend will
                            show alias names instead of daq_data labels.
                            None: plot all entries in daq_data, show basic labels in legend
            out_file_path - output file path, 
                            None: just show a (modal) dialog with plotted data 
                                  (mainly for debug purposes) 
            xlabel        - label for x-axis
            ylabel        - label for y-axis
            title         - title for plot/figure
            fig_size      - tuple with (<width>, <height>) values for plot/figure
            fig_dpi       - resolution (dpi) for stored pixel/raster images
    
    """
    if not daq_data:
        daq_data = {}
        
    fig = pyplot.figure(
        figsize=fig_size,
        tight_layout=True,
        # constrained_layout=True, # alternative to tight_layout
        # facecolor="#EEEEEE",
    )
    
    subplot = fig.add_subplot(111)
    
    subplot.set_title(title)
    subplot.set_xlabel(xlabel)
    subplot.set_ylabel(ylabel)
    subplot.grid(True)
    
    if not variables:
        # daq data may contain the same data referenced by multiple keys
        # (once as plain <name> and once with <device_name>.<name>)
        # => only plot unique variables/data
        variables = {}
        # order by length of variable name, so shorter names will be found first,
        # and longer names for the same data (i.e. with prefix) will be skipped.
        for name, entry in sorted(daq_data.items(), key=lambda item: len(item[0])):
            for existing_entry in variables.values():
                if entry is existing_entry:
                    print(f"# [skipped] {name}")
                    break
            else:
                # data not yet added: add now
                print(f"# [variable] {name}")
                variables[name] = entry
        
        variables = list(variables.keys())
    
    for var in variables:
        # use alias attribute instead of full representation/path, if available
        alias = getattr(var, "alias", str(var)) 
        if var not in daq_data:
            print(f"> {alias} not found in data, skipped")
            continue
        sig_data = daq_data[var]
        subplot.plot(sig_data["time"], sig_data["data"], label=alias)
    
    subplot.legend()
    
    if out_file_path:
        fig.savefig(out_file_path, bbox_inches="tight", dpi=fig_dpi)
    else:
        # pylab.show() opens a modal control, so it does not work that well 
        # during automatic tests (but it may be nice during debugging)
        pyplot.show()
    
    # release figure memory (might not work as well in older pylab releases)
    try:
        # using a tk backend to show interactive plots may raise exceptions on 
        # clear() in some matplotlib versions (e.g. TclError: invalid command name)
        # => does not matter that much here
        fig.clear()
    except Exception:
        pass
    pyplot.close() 
    

# #############################################################################
def demoPlot(daq_data, output_path="output.png"):
    """ Simple plotting of signals using matplotlib.
        
        Parameters:
            daq_data    - daq data structure containing data to display
            output_path - plotted data will be stored to this path 
    """
    # pyplot.xkcd()
    fig = pyplot.figure(
        figsize=(12, 4), 
        tight_layout=True,
    ) 
    subplot = fig.add_subplot(
        111, title="title", xlabel="time [s]", ylabel="values"
    )
    for sig_label, sig_data in sorted(daq_data.items()):
        subplot.plot(
            sig_data["time"], sig_data["data"], 
            label=sig_label, color=(0, 0.6, 0), marker="x", linestyle="-"
        )
    
    subplot.grid(True)
    subplot.legend()
    
    # store plot to file
    fig.savefig(output_path, dpi=96)
    
    # release figure memory (might not work as well in older pylab releases)
    fig.clear()
    pyplot.close()
    

# #############################################################################
#
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only example code)
    import os
    import tempfile
    import random
    
    random.seed(0) # static seed to get the same dummy data every time
    num_values = 120
    
    def rnd(x):
        return random.random() * 12 / max(1, abs(x - num_values / 2))
    
    daq_data = {
        "signal": {
            "time": [t * 0.001 for t in range(num_values)], 
            "data": [rnd(x)    for x in range(num_values)]
        }
    }
    
    path = os.path.join(tempfile.gettempdir(), "output.png")
    demoPlot(daq_data, path)
    
    #plotSignals(daq_data, out_file_path=path)
    
    os.startfile(path)
    
    print("Done.")
