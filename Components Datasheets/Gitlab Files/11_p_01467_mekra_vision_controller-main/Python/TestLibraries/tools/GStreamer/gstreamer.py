"""
.. module:: gstreamer
    :platform: Windows
    :synopsis: Stream, write to file and take pictures
"""

import subprocess
from pathlib import Path
import sys
import ipaddress

GST_LAUNCH_PATH = \
    'gstreamer_lib/bin/gst-launch-1.0.exe '
GST_STREAM_H264 = \
    'udpsrc port={} caps="application/x-rtp,media=video,encoding-name=H264,payload=96" ! ' \
    'rtpjitterbuffer ! rtph264depay ! h264parse ! openh264dec ! autovideosink sync=false async=false'
GST_STREAM_JPEG = \
    'udpsrc port={} caps="application/x-rtp,encoding-name=JPEG,clock-rate=90000,payload=26,framerate=30/1" ! ' \
    'rtpjitterbuffer ! rtpjpegdepay ! jpegparse ! jpegdec ! autovideosink sync=false async=false'
GST_RECORD_H264 = \
    'udpsrc port={} caps="application/x-rtp,media=video,encoding-name=H264,payload=96" ! ' \
    'rtpjitterbuffer ! rtph264depay ! h264parse ! openh264dec ! videorate ! video/x-raw,framerate=30/1 ! ' \
    'jpegenc quality={} ! avimux ! filesink location="{}.avi"'
GST_RECORD_JPEG = \
    'udpsrc port={} caps="application/x-rtp,encoding-name=JPEG,clock-rate=90000,payload=26,framerate=30/1" ! ' \
    'rtpjitterbuffer ! rtpjpegdepay ! jpegparse ! jpegdec ! videorate ! video/x-raw,framerate=30/1 ! ' \
    'jpegenc quality={} ! avimux ! filesink location="{}.avi"'
GST_PICTURE_H264 = \
    'udpsrc port={} caps="application/x-rtp,media=video,encoding-name=H264,payload=96" num-buffers=200 ! ' \
    'rtpjitterbuffer ! rtph264depay ! h264parse ! openh264dec ! ' \
    'jpegenc ! filesink location="{}.jpg"'
GST_PICTURE_H264_MULTICAST = \
    'udpsrc port={} multicast-group={} caps="application/x-rtp,media=video,encoding-name=H264,payload=96" num-buffers=200 ! ' \
    'rtpjitterbuffer ! rtph264depay ! h264parse ! openh264dec ! ' \
    'jpegenc ! filesink location="{}.jpg"'
GST_PICTURE_H264_TIFF = \
    'udpsrc port={} caps="application/x-rtp,media=video,encoding-name=H264,payload=96" num-buffers=200 ! ' \
    'rtpjitterbuffer ! rtph264depay ! h264parse ! openh264dec ! ' \
    'avenc_tiff ! filesink location="{}.tiff"'
GST_PICTURE_H264_BMP = \
    'udpsrc port={} caps="application/x-rtp,media=video,encoding-name=H264,payload=96" num-buffers=200 ! ' \
    'rtpjitterbuffer ! rtph264depay ! h264parse ! openh264dec ! ' \
    'videoconvert ! avenc_bmp ! filesink location="{}.bmp"'
GST_PICTURE_JPEG = \
    'udpsrc port={} caps="application/x-rtp,encoding-name=JPEG,clock-rate=90000,payload=26,framerate=30/1" ! ' \
    'rtpjitterbuffer ! rtpjpegdepay ! jpegparse ! jpegdec ! ' \
    'jpegenc snapshot=true ! filesink location="{}.jpg"'


class GStreamer:
    """
    Stream to seperate window / to a file or take a snapshot.
    """

    def __init__(self, output_folder):
        """
        :param output_folder: The folder to save files to.
        :type output_folder: str.
        """
        if not output_folder.endswith('/'):
            output_folder += '/'
        self.outputFolder = output_folder
        self.processes = []

    def __del__(self):
        """
        Terminates all processes.
        """
        for process in self.processes:
            process.terminate()

    def stream(self, port, encoding='JPEG', timeout=2):
        """
        :param timeout: timeout to kill subprocess
        :param port: The port to stream from.
        :type port: int.
        :param encoding: The encoding to use.
        :type encoding: str.
        :return: Popen.
        """
        if encoding == 'JPEG':
            pipeline = GST_STREAM_JPEG.format(port)
        elif encoding == 'H264':
            pipeline = GST_STREAM_H264.format(port)
        else:
            return None

        self.launch_pipeline(pipeline, timeout=timeout)
        
    def stream_background(self, port, encoding='JPEG'):
        """
        :param timeout: timeout to kill subprocess
        :param port: The port to stream from.
        :type port: int.
        :param encoding: The encoding to use.
        :type encoding: str.
        :return: Popen.
        """
        if encoding == 'JPEG':
            pipeline = GST_STREAM_JPEG.format(port)
        elif encoding == 'H264':
            pipeline = GST_STREAM_H264.format(port)
        else:
            return None

        self.launch_pipeline_background(pipeline)

    def record(self, port, filename, encoding='JPEG', quality=85, timeout=2):
        """
        :param timeout: timeout to kill subprocess
        :param port: The port to stream from.
        :type port: int.
        :param filename: The name of the file to be stored in outputFolder.
        :type filename: str.
        :param encoding: The encoding to use.
        :type encoding: str.
        :param quality: The compression quality (0 - 100).
        :type quality: int.
        :return: Popen.
        """
        if quality < 0 or quality > 100:
            return None

        if encoding == 'JPEG':
            pipeline = GST_RECORD_JPEG.format(port, quality, self.outputFolder + filename)
        elif encoding == 'H264':
            pipeline = GST_RECORD_H264.format(port, quality, self.outputFolder + filename)
        else:
            return None

        self.launch_pipeline(pipeline, timeout)

    def picture(self, port, filename, encoding='JPEG', timeout=5, streaming_dest_ip=None):
        """
        :param timeout: timeout to kill subprocess
        :param port: The port to stream from.
        :type port: int.
        :param filename: The name of the file to be stored in outputFolder.
        :type filename: str.
        :param encoding: The encoding to use.
        :type encoding: str.
        :return: Popen.
        """
        if encoding == 'JPEG':
            pipeline = GST_PICTURE_JPEG.format(port, self.outputFolder + filename)
        elif encoding == 'H264':
            if (streaming_dest_ip == None) or \
               (ipaddress.ip_address(streaming_dest_ip).is_private) or \
               (ipaddress.ip_address(streaming_dest_ip).is_reserved):
                pipeline = GST_PICTURE_H264.format(port, self.outputFolder + filename)
            elif ipaddress.ip_address(streaming_dest_ip).is_multicast:
                pipeline = GST_PICTURE_H264_MULTICAST.format(port, streaming_dest_ip, self.outputFolder + filename)
            else:
                return None
        elif encoding == 'H264_TIFF':
            pipeline = GST_PICTURE_H264_TIFF.format(port, self.outputFolder + filename)
        elif encoding == 'H264_BMP':
            pipeline = GST_PICTURE_H264_BMP.format(port, self.outputFolder + filename)
        else:
            return None
        try:
            self.launch_pipeline(pipeline, timeout)
        except subprocess.TimeoutExpired as te:
            print(f"timeout when receiving video stream via gstreamer, rtp-destination-port is set to {port}, is this correct?", file=sys.stderr)
            raise

    """
    @staticmethod
    def launch_pipeline(pipeline, timeout):
        gst_basepath = Path.joinpath(Path(__file__).parent, GST_LAUNCH_PATH)
        creationflags = subprocess.CREATE_NO_WINDOW  # execute subprocess without opening a command window

        result = subprocess.run(str(gst_basepath) + pipeline,
                                timeout=timeout,
                                creationflags=creationflags,
                                check=True)

        return result
    """
    """"""
    @staticmethod
    def launch_pipeline(pipeline, timeout):
        if getattr(sys, 'frozen', False):
            # In .exe: Verwende temporären Extraktionspfad
            base_path = sys._MEIPASS
        else:
            # In Entwicklung: Normaler Projektpfad
            base_path = Path(__file__).parent
        
        gst_basepath = Path(base_path) / GST_LAUNCH_PATH
        # ... rest unverändert
        creationflags = subprocess.CREATE_NO_WINDOW  # execute subprocess without opening a command window

        result = subprocess.run(str(gst_basepath) + pipeline,
                                timeout=timeout,
                                creationflags=creationflags,
                                check=True)

        return result
     
    @staticmethod
    def launch_pipeline_background(pipeline):
        gst_basepath = Path.joinpath(Path(__file__).parent, GST_LAUNCH_PATH)
        creationflags = subprocess.CREATE_NO_WINDOW  # kein Fenster öffnen

        # Starte den Prozess im Hintergrund
        process = subprocess.Popen(str(gst_basepath) + pipeline,
                                creationflags=creationflags)

        return process  # Du kannst den Prozess später beenden oder überwachen
   