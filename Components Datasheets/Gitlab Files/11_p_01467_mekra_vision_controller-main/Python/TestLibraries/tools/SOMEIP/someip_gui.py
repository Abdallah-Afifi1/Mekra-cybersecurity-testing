from tkinter import *
from tkinter import ttk, messagebox
import _thread
import sys
from Lib.SOMEIP.someip_client import SomeipClient
from Lib.SOMEIP.someip_packet import SomeipPacket
from Lib.General import helperModule


class SomeipClientGui:

    def __init__(self, master):
        self.master = master
        master.title("SOME/IP Client")

        self.number_of_clients = 0

        # Create new window for someip main application and construct a notebook which contains tabs to switch
        # between different clients
        self.main_gui = ttk.Notebook(self.master)
        self.main_gui.grid(column=0, row=0)

        self.someip_client_frames = []
        self.settings_frame = Frame(self.master)

        # Get config parameters
        config_parameters = SomeipClientGui.read_cfg()
        # Create settings menu
        self.settings_menu(config_parameters)

    def settings_menu(self, config_parameters):

        # Add settings tab
        self.main_gui.add(self.settings_frame, text="SOME/IP Client Configuration")
        someip_client_setting = \
            {
                "host_ip": StringVar(value=config_parameters.get("host_ip_cfg")),
                "ap0200_ip": StringVar(value=config_parameters.get("ap0200_ip_cfg")),
                "host_port": StringVar(value=config_parameters.get("host_port_cfg")),
                "server_port": StringVar(value=config_parameters.get("server_port_cfg")),
                "host_port_sd": StringVar(value=config_parameters.get("host_port_sd_cfg")),
                "multicast_ip": StringVar(value=config_parameters.get("multicast_ip_cfg"))
            }
        settings_window_width = 25
        settings_window_height = 1
        settings_window_anchor = "w"

        settings_gui = \
            [
                [
                    Label(self.settings_frame, text="Host IP Address:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(self.settings_frame, textvariable=someip_client_setting["host_ip"])
                ],
                [
                    Label(self.settings_frame, text="AP0200 IP Address:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(self.settings_frame, textvariable=someip_client_setting["ap0200_ip"])
                ],
                [
                    Label(self.settings_frame, text="Host Port:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(self.settings_frame, textvariable=someip_client_setting["host_port"])
                ],
                [
                    Label(self.settings_frame, text="Server Port:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(self.settings_frame, textvariable=someip_client_setting["server_port"])
                ],
                [
                    Label(self.settings_frame, text="Host Port SD:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(self.settings_frame, textvariable=someip_client_setting["host_port_sd"], state='disabled')
                ],
                [
                    Label(self.settings_frame, text="Multicast IP Address:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(self.settings_frame, textvariable=someip_client_setting["multicast_ip"], state='disabled')
                ],
                [
                    Button(self.settings_frame, text="Create", command=lambda: self.client_menu(
                        someip_client_setting), width=10)
                ]
            ]

        # Place defined gui objects into frame
        for row_index, row_element in enumerate(settings_gui):
            for col_index, col_element in enumerate(row_element):
                col_element.grid(column=col_index, row=row_index)

    def client_menu(self, settings):
        # Store new config parameters in cfg file
        SomeipClientGui.write_cfg(settings)
        # Gui settings
        settings_window_width = 25
        settings_window_height = 1
        settings_window_anchor = "w"

        # Create a someip client instance used for network communication
        try:
            someip_network_client = SomeipClient(client_ip=settings.get("host_ip").get(),
                                                 server_ip=settings.get("ap0200_ip").get(),
                                                 client_source_port=int(settings.get("host_port").get()),
                                                 client_destination_port=int(settings.get("server_port").get()))
        except ValueError:
            messagebox.showinfo("Error", "Wrong Parameters provided!")
            return

        self.number_of_clients += 1
        someip_client = Frame(self.master)
        self.someip_client_frames.append(someip_client)
        self.main_gui.add(someip_client, text="SOME/IP Client " + str(self.number_of_clients))

        # Change focus to this tab
        self.main_gui.select(someip_client)

        someip_header_parameters = \
            {
                "method_id": StringVar(),
                "service_id": StringVar(),
                "request_id": StringVar(value="0x12345678"),
                "protocol_version": StringVar(value="0x01"),
                "interface_version": StringVar(value="0x01"),
                "message_type": StringVar(value="0x00"),
                "return_code": StringVar(value="0x00"),
                "length": StringVar(),
                "length_default": IntVar(value=1),
                "method_id_default": IntVar(value=1),
                "service_id_default": IntVar(value=1)
            }
        someip_command_parameters = \
            {
                "subscribe_roi": StringVar(),
                "unsubscribe_roi": StringVar(),
                "getcam_control": StringVar(),
                "setcam_control": [StringVar(), StringVar(), StringVar(), StringVar()],
                "setcam_exclusive": StringVar()
            }

        # Define quit button
        quit_button = Button(someip_client, text="Close",
                             command=lambda: self.close_client(someip_client, someip_network_client), width=15)

        # Define scrollbar and listbox and label to show send and received messages
        message_log = Scrollbar(someip_client)
        message_log_x = Scrollbar(someip_client, orient=HORIZONTAL)
        listbox_log = Listbox(someip_client, height=30, width=70)
        listbox_label = Label(someip_client, text="Message Log:", height=settings_window_height)

        # Define Labels which represent the current configuration of the someip client which were set in the settings
        # menu

        settings_client = \
            [
                [
                    Label(someip_client, text="Host IP Address:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Label(someip_client, text=settings.get("host_ip").get(), anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width)
                ],
                [
                    Label(someip_client, text="AP0200 IP Address:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Label(someip_client, text=settings.get("ap0200_ip").get(), anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width)
                ],
                [
                    Label(someip_client, text="Host Port:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Label(someip_client, text=settings.get("host_port").get(), anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width)
                ],
                [
                    Label(someip_client, text="Server Port:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Label(someip_client, text=settings.get("server_port").get(), anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width)
                ],
                [
                    Label(someip_client, text="Host Port SD:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Label(someip_client, text=settings.get("host_port_sd").get(), anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width)
                ],
                [
                    Label(someip_client, text="Multicast IP Address:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Label(someip_client, text=settings.get("multicast_ip").get(), anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width)
                ]
            ]

        # Define Labels and Entries for someip header parameters
        settings_someip_header = \
            [
                [
                    # Empty label since grid ignores row indices where nothing is placed
                    Label(someip_client, text="", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                    Label(someip_client, text="", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                    Label(someip_client, text="Use default config", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width)
                ],
                [
                    Label(someip_client, text="Service ID:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("service_id"), state="disabled"),
                    Checkbutton(someip_client, text="", variable=someip_header_parameters.get("service_id_default"))
                ],
                [
                    Label(someip_client, text="Method ID:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("method_id"), state="disabled"),
                    Checkbutton(someip_client, text="", variable=someip_header_parameters.get("method_id_default"))
                ],
                [
                    Label(someip_client, text="Request ID:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("request_id"))
                ],
                [
                    Label(someip_client, text="Protocol Version:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("protocol_version"))
                ],
                [
                    Label(someip_client, text="Interface Version:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("interface_version"))
                ],
                [
                    Label(someip_client, text="Message Type:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("message_type"))
                ],
                [
                    Label(someip_client, text="Return Code:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("return_code"))
                ],
                [
                    Label(someip_client, text="Length:", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                    Entry(someip_client, textvariable=someip_header_parameters.get("length"), state="disabled"),
                    Checkbutton(someip_client, text="", variable=someip_header_parameters.get("length_default"))
                ]
            ]

        # Define callback function for length checkbutttons
        settings_someip_header[1][2].configure(command=lambda: self.checkbutton_callback(settings_someip_header[1][1]))
        settings_someip_header[2][2].configure(command=lambda: self.checkbutton_callback(settings_someip_header[2][1]))
        settings_someip_header[8][2].configure(command=lambda: self.checkbutton_callback(settings_someip_header[8][1]))

        # Define Labels and Entries for specific some ip messages
        settings_someip_messages = \
            [
                [
                    # Empty label since grid ignores row indices where nothing is placed
                    Label(someip_client, text="", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                ],
                [
                    Button(someip_client, text="SubscribeRoi",
                           command=lambda: self.prepare_sending(someip_network_client, 0,
                                                                someip_command_parameters.get("subscribe_roi"),
                                                                someip_header_parameters, listbox_log), width=15),
                    Label(someip_client, text="Roi index:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("subscribe_roi"))
                ],
                [
                    Button(someip_client, text="UnSubscribeRoi",
                           command=lambda: self.prepare_sending(someip_network_client, 1,
                                                                someip_command_parameters.get("unsubscribe_roi"),
                                                                someip_header_parameters, listbox_log), width=15),
                    Label(someip_client, text="Roi index:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("unsubscribe_roi"))
                ],
                [
                    Button(someip_client, text="GetCamStatus",
                           command=lambda: self.prepare_sending(someip_network_client, 2, None,
                                                                someip_header_parameters, listbox_log), width=15)
                ],
                [
                    Button(someip_client, text="GetCamControl",
                           command=lambda: self.prepare_sending(someip_network_client, 3,
                                                                someip_command_parameters.get("getcam_control"),
                                                                someip_header_parameters, listbox_log), width=15),
                    Label(someip_client, text="Control index:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("getcam_control"))
                ],
                [
                    Button(someip_client, text="SetCamControl",
                           command=lambda: self.prepare_sending(someip_network_client, 4,
                                                                someip_command_parameters.get("setcam_control"),
                                                                someip_header_parameters, listbox_log), width=15),
                    Label(someip_client, text="Control index:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("setcam_control")[0])
                ],
                [
                    Label(someip_client, text="", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                    Label(someip_client, text="Control mode:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("setcam_control")[1])
                ],
                [
                    Label(someip_client, text="", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                    Label(someip_client, text="Sup. control mode:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("setcam_control")[2])
                ],
                [
                    Label(someip_client, text="", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                    Label(someip_client, text="Control value:", anchor=settings_window_anchor,
                          height=settings_window_height, width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("setcam_control")[3])
                ],
                [
                    Button(someip_client, text="SetCamExclusive",
                           command=lambda: self.prepare_sending(someip_network_client, 5,
                                                                someip_command_parameters.get("setcam_exclusive"),
                                                                someip_header_parameters, listbox_log), width=15),
                    Label(someip_client, text="TTL:", anchor=settings_window_anchor, height=settings_window_height,
                          width=settings_window_width),
                    Entry(someip_client, textvariable=someip_command_parameters.get("setcam_exclusive"))
                ],
                [
                    Button(someip_client, text="EraseCamExclusive",
                           command=lambda: self.prepare_sending(someip_network_client, 6, None,
                                                                someip_header_parameters, listbox_log), width=15)
                ],
                [
                    Button(someip_client, text="FindService",
                           command=lambda: self.prepare_sending(someip_network_client, 7, None,
                                                                someip_header_parameters, listbox_log), width=15,
                           state="disabled")
                ]

            ]

        # Place client settings in someip client gui
        for row_index, row_element in enumerate(settings_client):
            for col_index, col_element in enumerate(row_element):
                col_element.grid(column=col_index, row=row_index, padx=(20, 0))

        # Place someip header settings in someip client gui except tooltip
        someip_header_row_offset = len(settings_client)

        for row_index, row_element in enumerate(settings_someip_header):
            for col_index, col_element in enumerate(row_element):
                if col_element == settings_someip_header[8][2] or col_element == settings_someip_header[0][2] or \
                        col_element == settings_someip_header[1][2] or col_element == settings_someip_header[2][2]:
                    col_element.grid(column=col_index, row=row_index + someip_header_row_offset, sticky=W)
                else:
                    col_element.grid(column=col_index, row=row_index + someip_header_row_offset, padx=(20, 0))

        # Place someip message settings in someip client gui
        someip_messages_row_offset = len(settings_someip_header) + len(settings_client)
        for row_index, row_element in enumerate(settings_someip_messages):
            for col_index, col_element in enumerate(row_element):
                col_element.grid(column=col_index, row=row_index + someip_messages_row_offset, pady=3, sticky=W,
                                 padx=(20, 0))

        # Place quit Button
        quit_button.grid(column=0,
                         row=len(settings_someip_header) + len(settings_client) + len(settings_someip_messages),
                         pady=(30, 30), sticky=W, padx=(20, 0))

        # Place scrollbar, listbox and label
        message_log.grid(column=4, row=len(settings_client) + 1,
                         rowspan=len(settings_someip_header) + len(settings_someip_messages) - 3, sticky=N + S,
                         padx=(0, 20))
        message_log_x.grid(column=3, row=len(settings_someip_header) + len(settings_someip_messages) + 4,
                           sticky=W + E + N, padx=(100, 0), pady=(3, 0))
        listbox_log.grid(column=3, row=len(settings_client) + 1,
                         rowspan=len(settings_someip_header) + len(settings_someip_messages), padx=(100, 0), sticky=N)
        listbox_label.grid(column=3, row=len(settings_client), padx=(100, 0))

        # attach listbox to scrollbar
        listbox_log.config(yscrollcommand=message_log.set, xscrollcommand=message_log_x.set)
        message_log.config(command=listbox_log.yview)
        message_log_x.config(command=listbox_log.xview)

    def close_client(self, someip_client, someip_network_client):
        del self.someip_client_frames[self.someip_client_frames.index(someip_client)]
        someip_network_client.close_socket()
        self.main_gui.forget(someip_client)

    def prepare_sending(self, someip_client, button_id, command_params, header_params, message_log):

        request_id = header_params.get("request_id").get()
        protocol_version = header_params.get("protocol_version").get()
        interface_version = header_params.get("interface_version").get()
        message_type = header_params.get("message_type").get()
        return_code = header_params.get("return_code").get()

        # Checkbutton handling for service id entry
        if header_params.get("service_id_default").get() == 1:
            service_id = 0x433F
        else:
            service_id = header_params.get("service_id").get()

        # Checkbutton handling for method id entry
        if header_params.get("method_id_default").get() == 1:
            if button_id == 0:
                method_id = 0x0131
            elif button_id == 1:
                method_id = 0x0132
            elif button_id == 2:
                method_id = 0x0002
            elif button_id == 3:
                method_id = 0x0203
            elif button_id == 4:
                method_id = 0x0201
            elif button_id == 5:
                method_id = 0x0011
            elif button_id == 6:
                method_id = 0x0019
            elif button_id == 7:
                method_id = 0xFFFF
            else:
                method_id = 0xFFFF
        else:
            method_id = header_params.get("method_id").get()

        # Checkbutton handling for length entry
        length_field = 0x0
        if header_params.get("length_default").get() == 1:
            if button_id == 0 or button_id == 1 or button_id == 5:
                length_field = 0xC
            elif button_id == 2 or button_id == 6:
                length_field = 0x8
            elif button_id == 3:
                length_field = 0x9
            elif button_id == 4:
                length_field = 0xD
        else:
            length_field = header_params.get("length").get()

        tx_packet = self.prepare_packet(someip_client, button_id, service_id, method_id, request_id, protocol_version,
                                        interface_version, message_type, return_code, length_field, command_params)

        if tx_packet:
            # Print packet content to message log
            tx_message = SomeipPacket.get_packet_stream(tx_packet)
            message_log.insert(END, "TX : " + " ".join(tx_message) + " (" + helperModule.get_human_readable_method_id(
                SomeipPacket.parse_someip_input(method_id)) + ")")
            self.on_add_log(message_log)

            _thread.start_new_thread(self.send_packet, (someip_client, tx_packet, message_log))

    @staticmethod
    def validate_someip_entries(action, inserted, posterior_content, prior_content):

        retval = False
        valid_characters = set("0123456789abcdefABCDEF")

        # Handle only insertions
        if action == "1":
            if set(inserted) <= valid_characters:
                print("inserted:", inserted, " posterior: ", posterior_content, " prior: ", prior_content)
                retval = True
            else:

                if len(posterior_content) > 1:
                    if (posterior_content[1] == "x" or posterior_content[1] == "X") and (
                            "x" not in inserted and "X" not in inserted):
                        retval = True
                    else:
                        retval = False
                else:
                    retval = False

        # Deletion is generally allowed
        elif action == "0":
            retval = True

        return retval

    @staticmethod
    def shutdown_application():
        print("shutting down application")

        exit()

    @staticmethod
    def read_cfg():
        config_file_name = "someip_gui.cfg"
        config_parameters = \
            {
                "ap0200_ip_cfg": "192.168.120.2",
                "host_ip_cfg": "192.168.120.1",
                "host_port_cfg": "5001",
                "server_port_cfg": "30501",
                "host_port_sd_cfg": "30490",
                "multicast_ip_cfg": "239.120.1.1"
            }

        try:
            config_file = open(sys.path[0] + "/" + config_file_name, 'r')
            config_file_lines = config_file.readlines()

            for curline in config_file_lines:
                curline = curline.rstrip()
                value = ""
                config_var = ""

                if "=" in curline:
                    config_var = curline.replace(" ", "").split("=")[0]
                    value = curline.replace(" ", "").split("=")[1]
                if config_var == "AP0200IPAddress":
                    config_parameters["ap0200_ip_cfg"] = value
                elif config_var == "HOSTIPAddress":
                    config_parameters["host_ip_cfg"] = value
                elif config_var == "HOSTPORT":
                    config_parameters["host_port_cfg"] = value
                elif config_var == "SERVERPORT":
                    config_parameters["server_port_cfg"] = value
                elif config_var == "HOSTPORT_SD":
                    config_parameters["host_port_sd_cfg"] = value
                elif config_var == "MULTICAST_IP":
                    config_parameters["multicast_ip_cfg"] = value

            config_file.close()

        except IOError:
            # Use default parameters if no config file found
            pass

        return config_parameters

    @staticmethod
    def write_cfg(someip_client_settings):
        config_file_name = "someip_gui.cfg"

        try:
            config_file = open(sys.path[0] + "/" + config_file_name, 'w')
            # Delete previous content
            config_file.seek(0)
            config_file.truncate()

            # Write new parameters
            config_file.write("AP0200IPAddress=" + someip_client_settings.get("ap0200_ip").get() + "\n")
            config_file.write("HOSTIPAddress=" + someip_client_settings.get("host_ip").get() + "\n")
            config_file.write("HOSTPORT=" + someip_client_settings.get("host_port").get() + "\n")
            config_file.write("SERVERPORT=" + someip_client_settings.get("server_port").get() + "\n")
            config_file.write("HOSTPORT_SD=" + someip_client_settings.get("host_port_sd").get() + "\n")
            config_file.write("MULTICAST_IP=" + someip_client_settings.get("multicast_ip").get() + "\n")
            config_file.close()
        except IOError:
            # Failed to open file => no writing possible
            pass

        return

    @staticmethod
    def checkbutton_callback(entry):
        if entry["state"] == "normal":
            entry["state"] = "disabled"
        elif entry["state"] == "disabled":
            entry["state"] = "normal"

    @staticmethod
    def prepare_packet(someip_client, button_id, service_id, method_id, request_id, protocol_version,
                       interface_version, message_type, return_code, length_field, command_params):
        tx_packet = None
        try:
            # SubscribeROI
            if button_id == 0:
                roi_index = command_params.get()
                tx_packet = someip_client.create_subscribe_roi_packet(roi_index,
                                                                      service_id=service_id,
                                                                      method_id=method_id,
                                                                      length=length_field,
                                                                      request_id=request_id,
                                                                      protocol_version=protocol_version,
                                                                      interface_version=interface_version,
                                                                      message_type=message_type,
                                                                      return_code=return_code)
            # UnSubscribeROI
            elif button_id == 1:
                roi_index = command_params.get()
                tx_packet = someip_client.create_unsubscribe_roi_packet(roi_index,
                                                                        service_id=service_id,
                                                                        method_id=method_id,
                                                                        length=length_field,
                                                                        request_id=request_id,
                                                                        protocol_version=protocol_version,
                                                                        interface_version=interface_version,
                                                                        message_type=message_type,
                                                                        return_code=return_code)
            # GetCamStatus
            elif button_id == 2:
                tx_packet = someip_client.create_get_cam_status_packet(service_id=service_id,
                                                                       method_id=method_id,
                                                                       length=length_field,
                                                                       request_id=request_id,
                                                                       protocol_version=protocol_version,
                                                                       interface_version=interface_version,
                                                                       message_type=message_type,
                                                                       return_code=return_code)
            # GetCamControl
            elif button_id == 3:
                control_index = command_params.get()
                tx_packet = someip_client.create_get_cam_control_packet(control_index,
                                                                        service_id=service_id,
                                                                        method_id=method_id,
                                                                        length=length_field,
                                                                        request_id=request_id,
                                                                        protocol_version=protocol_version,
                                                                        interface_version=interface_version,
                                                                        message_type=message_type,
                                                                        return_code=return_code)
            # SetCamControl
            elif button_id == 4:
                control_index = command_params[0].get()
                control_mode = command_params[1].get()
                supported_mode = command_params[2].get()
                control_value = command_params[3].get()
                tx_packet = someip_client.create_set_cam_control_packet(control_index,
                                                                        control_mode,
                                                                        supported_mode,
                                                                        control_value,
                                                                        service_id=service_id,
                                                                        method_id=method_id,
                                                                        length=length_field,
                                                                        request_id=request_id,
                                                                        protocol_version=protocol_version,
                                                                        interface_version=interface_version,
                                                                        message_type=message_type,
                                                                        return_code=return_code)
            # SetCamExclusive
            elif button_id == 5:
                ttl = command_params.get()
                tx_packet = someip_client.create_set_cam_exclusive_packet(ttl, service_id=service_id,
                                                                          method_id=method_id,
                                                                          length=length_field,
                                                                          request_id=request_id,
                                                                          protocol_version=protocol_version,
                                                                          interface_version=interface_version,
                                                                          message_type=message_type,
                                                                          return_code=return_code)
            # EraseCamExclusive
            elif button_id == 6:
                tx_packet = someip_client.create_erase_cam_exclusive_packet(service_id=service_id,
                                                                            method_id=method_id,
                                                                            length=length_field,
                                                                            request_id=request_id,
                                                                            protocol_version=protocol_version,
                                                                            interface_version=interface_version,
                                                                            message_type=message_type,
                                                                            return_code=return_code)
            # FindService
            elif button_id == 7:
                print("Not yet implemented")
        except (ValueError, OverflowError):
            messagebox.showinfo("Error", "Wrong Parameters provided!")

        return tx_packet

    def send_packet(self, someip_client, someip_packet, message_log):

        someip_client.send_packet(someip_packet, someip_client.serverIP, someip_client.destinationPort)

        # Write received message to log
        rx_packet = someip_client.someip_rx_packet
        if rx_packet:
            rx_message = SomeipPacket.get_packet_stream(rx_packet)
            message_log.insert(END, "RX : " + " ".join(rx_message) + " (" + helperModule.get_human_readable_return_code(
                rx_packet.get_return_code()) + ")")
            self.on_add_log(message_log)

            # additional readable infos for getCamStatus
            camstatus = helperModule.evaluate_camstatus(rx_packet)
            if str(camstatus[0]) != "":
                message_log.insert(END, "imager temp.: " + str(camstatus[0]) + "°C")
                message_log.insert(END, "power state input voltage: " + str(camstatus[1]))
                message_log.insert(END, "power state internal voltage: " + str(camstatus[2]))
                message_log.insert(END, "power state watchdog: " + str(camstatus[3]))
                message_log.insert(END, "power state luma: " + str(camstatus[4]))
                message_log.insert(END, "locked by: " + camstatus[5])
                self.on_add_log(message_log)

            # additional readable NTC value
            if someip_packet.get_payload() == "51":  # control 0x51 is NTC
                ntc_adc_value = rx_packet.get_payload()[-4:]
                message_log.insert(END, "NTC temp.: " + str(helperModule.parse_ntc_adc_value(ntc_adc_value)) + "°C")
                self.on_add_log(message_log)
        else:
            message_log.insert(END, "RX : Timeout")
            self.on_add_log(message_log)

    @staticmethod
    def on_add_log(message_log):
        message_log.yview(END)


root = Tk()
my_gui = SomeipClientGui(root)
root.mainloop()
